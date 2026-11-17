"""Signed channel diagnostics of the existing pure-SM RESPONSE amplitude.

No new cross-section formula, altered response table or channel mask is used.
The authoritative full prediction still comes from predict(backend='slow').
Channel pieces come directly from flavor_kernel_onebody_li2026().pieces;
phase space uses its existing public owner. Interference stays signed.
"""
import numpy as np
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.cross_section import amplitude_kernel_to_dsigma_cm2_per_GeV
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.rates.folding import linear_fold_weights
from cevns_pyeft.nuclear.response import ResponseDB

CHANNELS=('M','SigmaPP','SigmaP','PhiPP','PhiPT','Delta','MPhiPP','SigmaPDelta')


def decompose(model, arrays, numerical, *, sin2thetaW):
    """Return (nucleus,flavor,channel,PE) before time, with closure checks.

    E^2*dSigma_channel/dT is checked at five physical energies: three define
    a quadratic and two are independent holdouts. This is SM-only, diagnostic
    evaluation; failure raises instead of silently extrapolating a channel.
    Full Slow counts are independently computed and must agree after summing.
    """
    interaction=model.interaction
    db=ResponseDB(interaction.responses_json)
    left=_sm_left_dim6(True,sin2thetaW)
    fluence=model.source.for_run(model.run)
    energy_parts=np.zeros((2,3,len(CHANNELS),9))
    yield_arrays={}
    audit=dict(probe_calls=0,max_polynomial_relative_error=0.,max_cross_section_sum_relative_error=0.,
               max_recoil_yield_relative_error=0.,max_folded_bin_absolute_error=0.,
               signed_interference_preserved=True,formula_owner='existing amplitude.pieces and phase-space converter',
               particle_convention='unchanged native legacy_shared_kernel; no new antineutrino helicity convention')
    for it,target in enumerate(model.targets.isotopes):
        response=db.get(interaction.response_keys[target.isotope_id])
        stem=target.isotope_id+'_'+fluence.components[0].component_id
        recoil=arrays[stem+'_T_keVnr']
        yields=np.zeros((3,len(CHANNELS),len(recoil)))
        hi=max(c.support.integration_domain_MeV[1] for c in fluence.components)

        def evaluate(energy,T):
            result=flavor_kernel_onebody_li2026(response,E_nu_GeV=float(energy)*1e-3,
                ER_keV=float(T),left_hat=left,basis='np',c10_mass_mode=interaction.c10_mass_mode)
            matrices=np.array([result.pieces[name] for name in CHANNELS])
            # Pure SM is flavor universal. Verify this at every actual probe.
            diag=matrices[:,0,0]
            scale=max(float(abs(result.kernel).max()),1e-300)
            np.testing.assert_allclose(matrices,diag[:,None,None]*np.eye(3),rtol=0,atol=scale*2e-13)
            assert abs(diag.imag).max() < scale*2e-13
            pref=amplitude_kernel_to_dsigma_cm2_per_GeV(np.eye(3),E_nu_GeV=float(energy)*1e-3,
                m_A_GeV=target.kinematic_mass_GeV)[0,0].real*1e-6
            values=diag.real*pref
            total=result.kernel[0,0].real*pref
            err=abs(values.sum()-total)/max(abs(total),1e-300)
            audit['max_cross_section_sum_relative_error']=max(audit['max_cross_section_sum_relative_error'],float(err))
            assert err<2e-12
            audit['probe_calls']+=1
            return values

        for ir,T in enumerate(recoil):
            minimum=interaction.kinematics.minimum_energy_MeV(target,float(T))
            if hi-minimum>1e-8:
                probes=minimum+(hi-minimum)*np.array([.10,.31,.52,.73,.94])
                measured=np.array([evaluate(e,T) for e in probes])
                scale=max(float(abs(measured*probes[:,None]**2).max()),1e-300)
                coefficients=np.polynomial.polynomial.polyfit(probes[[0,2,4]]/hi,
                    measured[[0,2,4]]*probes[[0,2,4],None]**2/scale,2)
                test=np.polynomial.polynomial.polyval(probes/hi,coefficients).T*scale/probes[:,None]**2
                err=float(abs(test-measured).max()/max(abs(measured).max(),1e-300))
                audit['max_polynomial_relative_error']=max(audit['max_polynomial_relative_error'],err)
                np.testing.assert_allclose(test,measured,rtol=2e-10,atol=2e-12*abs(measured).max())
                for jf,component in enumerate(fluence.components):
                    lo,high=component.support.integration_domain_MeV
                    grid=np.unique(np.r_[np.linspace(lo,high,numerical.n_enu),component.support.breakpoints_MeV])
                    grid=grid[(grid>=minimum)&(grid>0)]
                    if grid.size:
                        cross=np.polynomial.polynomial.polyval(grid/hi,coefficients)*scale/grid[None,:]**2
                        yields[jf,:,ir]=np.trapezoid(cross*component.continuum(grid)[None,:],grid,axis=1)
            for jf,component in enumerate(fluence.components):
                for line in component.lines:
                    if line.energy_MeV>=minimum:
                        yields[jf,:,ir]+=line.fluence_per_cm2*evaluate(line.energy_MeV,T)
        matrix=linear_fold_weights(target,model.observation,model.binning,numerical,recoil,fluence.components[0].component_id)
        for jf,component in enumerate(fluence.components):
            ref=arrays[target.isotope_id+'_'+component.component_id+'_yield_per_keV_per_nucleus']
            err=float(abs(yields[jf].sum(axis=0)-ref).max()/max(abs(ref).max(),1e-300))
            audit['max_recoil_yield_relative_error']=max(audit['max_recoil_yield_relative_error'],err)
            np.testing.assert_allclose(yields[jf].sum(axis=0),ref,rtol=2e-10,atol=abs(ref).max()*2e-12)
            # The adopted pre-time selection is unity for all three components.
            assert model.observation.selection.acceptance(component.component_id)==1.
            energy_parts[it,jf]=yields[jf]@matrix*target.number_of_nuclei
        yield_arrays[target.isotope_id+'_channel_recoil_yields_per_nucleus_keV']=yields
    difference=energy_parts.sum(axis=2)-arrays['energy_before_time']
    audit['max_folded_bin_absolute_error']=float(abs(difference).max())
    np.testing.assert_allclose(energy_parts.sum(axis=2),arrays['energy_before_time'],rtol=2e-10,atol=2e-9)
    return energy_parts,yield_arrays,audit
