"""Paper-theme v4 figures for the RESPONSE-only forward calculation."""
import numpy as np


def draw(z,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import AutoMinorLocator
    from plotting.paper_theme.plot_template import configure,load_theme,style_axis
    from examples.COHERENT_CsI.time_resolved_sm.response_decomposition import CHANNELS
    theme=load_theme();configure(theme);ink=theme.cfg['colors']['ink']
    pe,te=z['pe_edges'],z['time_edges_us']
    labels=[r'$\nu_\mu$',r'$\nu_e$',r'$\bar\nu_\mu$','BRN','NIN']
    colors=[theme.palette[i]['color'] for i in range(5)]
    def components(shift):
        stem=f'reference_window_{shift:+g}ns'
        return np.concatenate([z[stem+'_target_flavor_counts'].sum(axis=0),
            z[stem+'_prior_posteff_BRN'][None],z[stem+'_prior_posteff_NIN'][None]])
    def style(ax,tag,last=True):
        style_axis(ax,theme);ax.set_xlim(0,60 if tag=='PE' else 6)
        if last:ax.set_xlabel('Reconstructed photoelectrons [PE]' if tag=='PE' else r'Reconstructed time [$\mu\mathrm{s}$]')
        else:ax.tick_params(labelbottom=False)
    def save(fig,name):
        fig.canvas.draw();rr=fig.canvas.get_renderer()
        for ax in fig.axes:
            texts=[ax._left_title,ax.xaxis.label,ax.yaxis.label]
            texts += [t for t,v in zip(ax.get_xticklabels(),ax.get_xticks()) if ax.get_xlim()[0]<=v<=ax.get_xlim()[1]]
            texts += [t for t,v in zip(ax.get_yticklabels(),ax.get_yticks()) if ax.get_ylim()[0]<=v<=ax.get_ylim()[1]]
            for t in texts:
                if t.get_visible() and t.get_text():
                    b=t.get_window_extent(rr);assert b.x0>=0 and b.y0>=0 and b.x1<=fig.bbox.x1 and b.y1<=fig.bbox.y1,(name,t.get_text())
        for legend in fig.legends:
            b=legend.get_window_extent(rr)
            assert all(not b.overlaps(ax.get_tightbbox(rr)) for ax in fig.axes),name+' legend overlap'
        for ext in ('pdf','png','svg'):fig.savefig(out/(name+'.'+ext),dpi=300,bbox_inches=None)
        plt.close(fig)
    # 1. Original requested stacked layout, with both data-error definitions visible.
    fig,axs=plt.subplots(2,2,figsize=(180/25.4,145/25.4))
    fig.subplots_adjust(left=.095,right=.985,bottom=.10,top=.80,wspace=.30,hspace=.33)
    for row,shift in enumerate((0,75)):
        comp=components(shift)
        for col,(tag,edges,axis) in enumerate([('PE',pe,2),('time_us',te,1)]):
            ax=axs[row,col];w=np.diff(edges);x=(edges[:-1]+edges[1:])/2;v=comp.sum(axis=axis);bottom=np.zeros_like(w)
            for f in (3,4,0,2,1):
                ax.bar(edges[:-1],v[f]/w,width=w,align='edge',bottom=bottom,zorder=2,**theme.bar_style(f))
                bottom+=v[f]/w
            ax.stairs(bottom,edges,color=ink,lw=1.1,zorder=3)
            ax.stairs(z['paper_'+tag+'_component_events'].sum(axis=0)/w,edges,color=ink,ls='--',lw=1.2,zorder=4)
            ax.errorbar(x,z['paper_'+tag+'_data_density'],
                yerr=[z['paper_'+tag+'_data_error_minus_density'],z['paper_'+tag+'_data_error_plus_density']],
                fmt='o',color=ink,ms=2.7,capsize=1.5,elinewidth=.65,zorder=6)
            obs=(z['C_raw']-z['SS_derived']).sum(axis=axis-1)
            sigma=np.sqrt(np.diag(z['PE_covariance' if col==0 else 'time_covariance']))
            ax.errorbar(x,obs/w,yerr=sigma/w,fmt='s',color=colors[1],mfc='white',ms=2.6,capsize=1.4,elinewidth=.6,zorder=5)
            ax.set_title(f'({chr(97+row*2+col)}) RESPONSE, '+(r'$\Delta t=0$ ns' if shift==0 else r'$\Delta t=+75$ ns'),loc='left',fontsize=9,pad=5)
            ax.set_ylabel('Events / PE' if col==0 else r'Events / $\mu\mathrm{s}$');style(ax,tag)
    handles=[Patch(facecolor=theme.palette[i]['bar_fill'],label=labels[i]) for i in range(5)]
    handles += [Line2D([],[],color=ink,lw=1.1,label='RESPONSE total'),Line2D([],[],color=ink,ls='--',label='Paper prediction'),
        Line2D([],[],color=ink,marker='o',ls='none',ms=3,label='Paper residual'),
        Line2D([],[],color=colors[1],marker='s',mfc='white',ls='none',ms=3,label=r'Local $C-\widehat{\mathrm{SSB}}$')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,.995),ncol=5,fontsize=8)
    fig.text(.54,.862,'Reference-window fluence; neutrons: prior_posteff; +75 ns diagnostic',ha='center',fontsize=8)
    save(fig,'Figure_RESPONSE_Stacked_Comparison')
    # 2. Each flavor/background separately: nominal and diagnostic vs paper.
    fig,axs=plt.subplots(4,2,figsize=(180/25.4,205/25.4))
    fig.subplots_adjust(left=.10,right=.985,bottom=.08,top=.89,wspace=.30,hspace=.48)
    for row in range(4):
        for col,(tag,edges,axis) in enumerate([('PE',pe,2),('time_us',te,1)]):
            ax=axs[row,col];w=np.diff(edges)
            for shift,ls in [(0,':'),(75,'-')]:
                c=components(shift).sum(axis=axis);vals=c[row] if row<3 else c[3:].sum(axis=0)
                ax.stairs(vals/w,edges,color=colors[row],ls=ls,lw=1.5)
            ax.stairs(z['paper_'+tag+'_component_events'][row]/w,edges,color=ink,ls='--',lw=1.1)
            ax.set_title(f'({chr(97+2*row+col)}) '+(labels[row] if row<3 else 'BRN + NIN'),loc='left',pad=5)
            ax.set_ylabel('Events / PE' if col==0 else r'Events / $\mu\mathrm{s}$');ax.set_ylim(bottom=0);style(ax,tag,row==3)
    fig.legend([Line2D([],[],color=ink,ls=':',lw=1.5),Line2D([],[],color=ink,lw=1.5),Line2D([],[],color=ink,ls='--',lw=1.1)],
        ['RESPONSE, 0 ns','RESPONSE, +75 ns (diagnostic)','Paper Fig.1 component'],loc='upper center',bbox_to_anchor=(.54,.99),ncol=2,fontsize=8)
    fig.text(.54,.925,'Reference-window fluence; neutrons: prior_posteff; no flavor rescaling',ha='center',fontsize=8)
    save(fig,'Figure_RESPONSE_Paper_Components')
    # 3. Signed nuclear-response contributions, including exact zeros.
    ch=z['reference_window_+0ns_target_flavor_channel_counts'].sum(axis=(0,1))
    totals=ch.sum(axis=(1,2))
    clabels=[r'$M$',r'$\Sigma^{\prime\prime}$',r'$\Sigma^{\prime}$',r'$\Phi^{\prime\prime}$',
        r'$\widetilde\Phi^{\prime}$',r'$\Delta$',r'$M\Phi^{\prime\prime}$',r'$\Sigma^{\prime}\Delta$']
    fig,axs=plt.subplots(1,2,figsize=(180/25.4,105/25.4))
    fig.subplots_adjust(left=.13,right=.985,bottom=.22,top=.80,wspace=.42)
    ax=axs[0];y=np.arange(8)
    for k in range(8):ax.barh(k,totals[k],height=.68,color=theme.palette[(5+k)%12]['bar_fill'],edgecolor='white',lw=.5)
    ax.set_yticks(y,clabels);ax.invert_yaxis();ax.set_xscale('symlog',linthresh=.01)
    ax.axvline(0,color=ink,lw=.7);ax.set_xlabel('Signed accepted events (symlog)')
    ax.set_title('(a) All RESPONSE channels',loc='left',pad=6);ax.grid(axis='x',color=theme.cfg['colors']['grid'],lw=.45)
    ax=axs[1];handles=[]
    for k in range(1,8):
        if abs(ch[k]).max()<1e-12:continue
        color=theme.palette[(5+k)%12]['color'];ls=['-', '--', ':', '-.'][k%4]
        vals=ch[k].sum(axis=1)
        ax.stairs(vals,pe,color=color,ls=ls,lw=1.4)
        handles.append(Line2D([],[],color=color,ls=ls,lw=1.4,label=clabels[k]))
    ax.axhline(0,color=ink,lw=.7);ax.set_xlim(0,60);ax.set_xlabel('Reconstructed photoelectrons [PE]')
    ax.set_ylabel('Signed events / bin');ax.set_title('(b) Channels other than M',loc='left',pad=6);style_axis(ax,theme)
    if handles:fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.54,.99),ncol=4,fontsize=8)
    fig.text(.55,.09,'0 ns; reference-window fluence; full M is not the legacy M+c1 truncation',ha='center',fontsize=8)
    fig.text(.55,.04,'Signed interference retained; channel sum checked against independent native Slow prediction',ha='center',fontsize=8)
    save(fig,'Figure_RESPONSE_Channel_Contributions')
