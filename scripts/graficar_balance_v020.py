"""Figuras del balance a partir de JSON reales (matplotlib opcional)."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter,FuncFormatter
    before=json.loads((ROOT/'resultados/balance_v020/antes_v019.json').read_text())
    after=json.loads((ROOT/'resultados/balance_v020/despues_v020.json').read_text())
    curves=json.loads((ROOT/'resultados/convergencia_v020/resumen_v020.json').read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(11,7.7),layout='constrained')
    for axis,key,title in [(axes[0,0],'used_wargreymon','Aventuras que utilizan WarGreymon'),(axes[0,1],'wins','Victorias desde el inicio')]:
        for i,(label,source,color) in enumerate([('v0.19',before,'#8895A7'),('v0.20',after['form_metrics'],'#168A98')]):
            values=[sum(r[key] for r in source[n])/sum(r['episodes'] for r in source[n]) for n in ('dp','mc')]
            positions=[j+(i-.5)*.34 for j in (0,1)]
            bars=axis.bar(positions,values,width=.31,label=label,color=color)
            axis.bar_label(bars,labels=[f'{v:.1%}'.replace('.',',') for v in values],padding=4,fontsize=10)
        axis.set(title=title,xticks=[0,1],xticklabels=['DP','MC (60.000 episodios)'],ylim=(0,1.08))
        axis.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));axis.legend(frameon=False,loc='lower right')
    data=curves['by_checkpoint'];x=[r['checkpoint'] for r in data]
    for axis,key,title in [(axes[1,0],'mc_win_rate','Aprendizaje MC · reglas v0.20'),(axes[1,1],'mc_state_coverage','Cobertura MC · reglas v0.20')]:
        axis.errorbar(x,[r[key]['mean'] for r in data],yerr=[r[key]['std'] for r in data],fmt='o-',color='#168A98',capsize=4,label='MC ±1 DE')
        if key=='mc_win_rate':
            axis.axhline(data[0]['dp_win_rate']['mean'],color='#666666',ls='--',label='DP de referencia')
            axis.set_ylim(0,1.03)
        else:axis.set_ylim(0,.32)
        axis.set(title=title,xlabel='Episodios de entrenamiento MC',xlim=(0,21500))
        axis.set_xticks([0,5000,10000,15000,20000]);axis.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{int(v):,}'.replace(',','.')))
        axis.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));axis.legend(frameon=False)
    for ax in axes.flat:ax.set_axisbelow(True);ax.grid(axis='y',color='#DDDDDD',lw=.6)
    fig.suptitle('Digimon RPG · balance de Piedmon y digievolución final',fontsize=16,fontweight='bold')
    destination=ROOT/'docs/figuras_v020';destination.mkdir(parents=True,exist_ok=True)
    fig.savefig(destination/'balance_y_aprendizaje.png',dpi=180)
    fig.savefig(destination/'balance_y_aprendizaje.svg')
    plt.close(fig)
if __name__=='__main__':main()
