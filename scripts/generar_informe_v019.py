"""Actualiza el borrador v0.13 conservando estilos, estructura y ecuaciones OMML.

Requiere python-docx y matplotlib solo para editar el informe, no para jugar.
No entrena agentes ni modifica políticas o resultados experimentales.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]


def create_chart(summary,destination):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter,FuncFormatter
    data=summary['by_checkpoint'];x=[v['checkpoint'] for v in data]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,
                         'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(7.1,5.3),sharex=True,layout='constrained')
    y=[v['mc_win_rate']['mean'] for v in data];sd=[v['mc_win_rate']['std'] for v in data]
    axes[0].errorbar(x,y,yerr=sd,fmt='o-',capsize=4,lw=1.7,color='#165C83',label='Monte Carlo')
    dp=data[0]['dp_win_rate']['mean'];dp_sd=data[0]['dp_win_rate']['std']
    axes[0].axhspan(dp-dp_sd,dp+dp_sd,color='#707070',alpha=.12)
    axes[0].axhline(dp,color='#555555',ls='--',lw=1.3,label='DP de referencia')
    axes[0].set(title='Victoria desde el estado inicial',ylabel='Tasa de victoria',ylim=(0,1.05))
    axes[0].legend(loc='lower right',frameon=False)
    for xx,yy in zip(x,y):
        axes[0].annotate(f'{yy:.1%}'.replace('.',','),(xx,yy),xytext=(7,9),textcoords='offset points',fontsize=8)
    coverage=[v['mc_state_coverage']['mean'] for v in data]
    coverage_sd=[v['mc_state_coverage']['std'] for v in data]
    axes[1].errorbar(x,coverage,yerr=coverage_sd,fmt='s-',capsize=4,lw=1.7,color='#2F6D4F')
    axes[1].set(title='Cobertura de estados de Monte Carlo',ylabel='Estados actualizados',
                xlabel='Episodios acumulados de entrenamiento MC',ylim=(0,.31),xlim=(0,22000))
    axes[1].set_xticks(x)
    axes[1].xaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{int(v):,}'.replace(',','.')))
    for ax in axes:
        ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
        ax.grid(axis='y',color='#D9D9D9',lw=.6);ax.set_axisbelow(True)
    fig.savefig(destination,dpi=240)
    fig.savefig(destination.with_suffix('.svg'))
    plt.close(fig)


def main():
    if (ROOT/"politicas/historico_v019").exists():
        raise SystemExit("El Word v0.19 es histórico. Para regenerarlo usa el ZIP v0.19; para el balance actual consulta docs/balance_v020.md.")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toc-json',type=Path)
    args=parser.parse_args()
    from docx import Document
    from docx.shared import Inches,Pt,RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_TAB_ALIGNMENT,WD_TAB_LEADER
    from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    summary=json.loads((ROOT/'resultados/convergencia_v011/resumen_v011.json').read_text())
    main_eval=json.loads((ROOT/'resultados/validacion_v0_9.json').read_text())
    figures=ROOT/'docs/figuras_v019';figures.mkdir(exist_ok=True)
    chart=figures/'curvas_lineales_v019.png';create_chart(summary,chart)
    screenshot=figures/'interfaz_v019.png'
    if not screenshot.is_file():
        raise FileNotFoundError('Incluye primero una captura real del mapa en docs/figuras_v019/interfaz_v019.png')
    doc=Document(ROOT/'docs/Informe_Final_Digimon_RPG_Borrador_v013.docx')
    original=list(doc.paragraphs)
    doc.core_properties.author='Diego Droguett'
    doc.core_properties.title='Digimon RPG La corrupción del Mundo Digital'
    doc.core_properties.subject='Comparación de Value Iteration y Monte Carlo en COM50100'
    doc.styles['Normal'].paragraph_format.space_after=Pt(6)
    for name in ('Title','Subtitle','Heading 1','Heading 2','Heading 3'):
        doc.styles[name].font.color.rgb=RGBColor(0,0,0)
    original[7].text='Estudiante   Diego Droguett'
    original[9].text='Fecha   5 de noviembre de 2026'
    original[10].text='Versión del proyecto   0.19 sobre la base 0.18'
    original[11].text='Informe actualizado para revisión académica'
    original[24].text += ' La bibliografía obligatoria del programa incluye a Sutton y Barto como referencia de estos métodos [5].'
    original[36].text=original[36].text.replace('acciones con mayor Q.','acciones con mayor Q, con desempate aleatorio.')
    original[43].text=('La separación entre el motor, los agentes y la vista mantiene una única definición del problema. '
        'La interfaz permite inspeccionar el estado y las decisiones sin entrenar durante el renderizado. '
        'Los cambios de presentación de las versiones 0.13 a 0.19 conservan el motor y las políticas [4].')
    original[51].text=('La validación de software registra 161 pruebas aprobadas. Las pruebas gráficas y de audio '
        'se ejecutaron con Pygame 2.6.1 en Linux y controladores SDL dummy; no equivalen a una prueba física '
        'de altavoces ni a la ejecución nativa en Windows. El paquete incluye VALIDAR_WINDOWS.bat para '
        'registrar esa comprobación en el equipo de destino.')
    original[55].text=('La exploración con ε = 0,15 se mantiene durante el entrenamiento; la evaluación '
        'usa una política greedy congelada. Por eso sus desempeños no son intercambiables. La variabilidad '
        'entre cinco semillas es descriptiva: la desviación estándar no es un intervalo de confianza. '
        'Las curvas no prueban convergencia formal ni que Q haya alcanzado una política óptima determinista.')
    original[56].text=('No hubo truncamientos en las corridas registradas. El código los cuenta y excluye '
        'sus retornos de la actualización MC; si fueran frecuentes, habría que estudiar el sesgo de usar '
        'solo episodios completos. También se distingue un estado no visitado de una acción cuyo Q sigue en cero.')
    original[59].text=('El cierre operativo requiere registrar la validación nativa en Windows, incorporar '
        'la URL pública de entrega y ensayar la exposición de diez minutos. Las mediciones de aprendizaje '
        'permanecen separadas de la evidencia de interfaz y audio.')
    original[62].text=original[62].text.replace('Material docente','Diapositivas sobre control on-policy y políticas suaves. Material docente')
    original[64].text=('[4] Droguett, D. (2026). Digimon RPG La corrupción del Mundo Digital. '
        'Código Python v0.19, políticas del MDP v0.9 y resultados reproducibles v0.11 incluidos en el paquete.')

    def before(anchor,text='',style=None):
        p=anchor.insert_paragraph_before(text,style)
        return p

    def heading(anchor,text,level=2,new_page=False):
        p=before(anchor,text,f'Heading {level}')
        p.paragraph_format.page_break_before=new_page
        return p

    def paragraph(anchor,text,caption=False):
        p=before(anchor,text)
        if caption:
            p.paragraph_format.space_after=Pt(9)
            for r in p.runs:r.font.size=Pt(10)
        return p

    def picture(anchor,path,width=6.8):
        p=before(anchor);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next=True
        p.add_run().add_picture(str(path),width=Inches(width))

    anchor=original[44]
    heading(anchor,'Interfaz del videojuego',new_page=True)
    paragraph(anchor,'El mapa representa siete regiones conectadas. Cada región agrupa numerosos estados: '
        'la salud, energía, forma, poción y demás variables distinguen situaciones distintas dentro de ella. '
        'Los marcadores del mapa no son los 48.553 estados del MDP.')
    picture(anchor,screenshot)
    paragraph(anchor,'Figura 1. Interfaz actual del juego y rutas del Mundo Digital. Captura de una trayectoria '
        'real hasta despejar el Pantano, ejecutada en modo manual con acciones de la política DP guardada '
        '(semilla base 42). Es evidencia de interfaz y no una evaluación adicional de aprendizaje.',True)
    paragraph(anchor,'CombatAnimation y TurnFeedback presentan el daño y la curación de un turno ya resuelto. '
        'WorldMapView obtiene el recorrido del historial; AudioManager reproduce 23 efectos locales. '
        'Los relojes de animación, audio y viajes no forman parte del estado observado por los agentes '
        'ni modifican probabilidades, recompensas o muestreos. F4 consulta los resultados, F5 guía la '
        'presentación, F6 muestra habilidades y T permite inspeccionar políticas y valores Q.')

    anchor=original[52]
    heading(anchor,'Curvas de aprendizaje',new_page=True)
    picture(anchor,chart)
    paragraph(anchor,'Figura 2. Medias de cinco semillas y barras de ±1 desviación estándar muestral. '
        'La banda gris corresponde a la referencia DP evaluada por semilla, no a un entrenamiento de DP '
        'en cada punto. El eje horizontal usa las cantidades reales de episodios. Cobertura significa '
        'estados con al menos un par estado acción actualizado dividido por 48.553. Fuente: '
        'resultados/convergencia_v011/resumen_v011.json.',True)
    paragraph(anchor,'La tasa de victoria y la cobertura describen aspectos distintos. Una política puede '
        'ganar con frecuencia desde el inicio fijo y seguir sin tener información para gran parte del '
        'espacio alcanzable. El uso de respaldo medio al final del experimento es 0,19 % de las acciones; '
        'por eso se informa junto con el rendimiento y no solo el porcentaje de victorias.')
    heading(anchor,'Evaluación de las políticas incluidas',new_page=True)
    paragraph(anchor,'El paquete permite jugar con políticas guardadas. Su evaluación histórica v0.9 utiliza '
        '500 partidas por método, semilla de evaluación 2042 y γ = 0,95. MC se entrenó por separado con '
        '60.000 episodios y semilla 42. La siguiente tabla no es un punto adicional de las curvas multisemilla.')
    table=doc.add_table(rows=1,cols=4);table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
    headers=('Política guardada','Estados con política','Victorias sobre 500','Retorno descontado medio')
    for c,value in zip(table.rows[0].cells,headers):c.text=value
    for key,label in (('dp','Value Iteration'),('mc','Monte Carlo')):
        value=main_eval[key];row=table.add_row()
        cells=(label,f"{value['trained_policy_states']:,}".replace(',','.'),
               f"{value['wins']}/500 ({value['win_rate']:.1%})".replace('.',','),
               f"{value['mean_discounted_return']:.2f}".replace('.',','))
        for cell,value in zip(row.cells,cells):cell.text=value
    # Reutiliza el formato del informe base y sus bordes y márgenes verificados.
    base=doc.tables[2]
    widths=(1.55,1.55,1.85,1.85)
    for i,row in enumerate(table.rows):
        for j,cell in enumerate(row.cells):
            cell.width=Inches(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            source=base.rows[min(i,1)].cells[0]._tc.tcPr
            own=cell._tc.get_or_add_tcPr()
            for tag in ('tcBorders','tcMar','shd'):
                for node in list(own.findall(qn('w:'+tag))):own.remove(node)
                node=source.find(qn('w:'+tag))
                if node is not None:own.append(deepcopy(node))
            for p in cell.paragraphs:
                p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(3)
                p.paragraph_format.line_spacing=1.05
                p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:r.font.size=Pt(10);r.bold=i==0
    table._tbl.getparent().remove(table._tbl);anchor._p.addprevious(table._tbl)
    paragraph(anchor,'Tabla 2. Evaluación histórica de las políticas utilizadas por el juego. Fuente: '
        'resultados/validacion_v0_9.json y metadatos de politicas/dp.json y politicas/mc.json.',True)
    paragraph(anchor,'La diferencia entre 90,6 % de esta evaluación MC y 82,6 % del último punto de las '
        'curvas no estima por sí sola el efecto de entrenar más. Cambian el presupuesto, las semillas '
        'y las partidas de evaluación. En las 500 partidas registradas MC usó dos acciones de respaldo '
        'y DP ninguna; ninguno registró truncamientos.')
    heading(anchor,'Verificación del videojuego')
    paragraph(anchor,'Las 161 pruebas automatizadas incluyen validez de acciones, normalización de '
        'transiciones, límites del estado, First-Visit, continuidad de entrenamiento, persistencia de '
        'políticas y navegación de la interfaz. El análisis estático no detecta bibliotecas de aprendizaje '
        'reforzado; por sí solo no constituye una prueba matemática del algoritmo.')
    paragraph(anchor,'Las siete regiones, cuatro formas, trece efectos gráficos y 23 WAV se probaron '
        'mediante diagnósticos SDL. Se verificó que dibujar, cambiar volumen, escuchar habilidades '
        'y omitir animaciones no consuman un turno adicional ni alteren el RNG. Las capturas, videos '
        'y verificaciones de archivos se conservan como evidencia de software, separada de las curvas.')
    ref=paragraph(original[64],'[5] Universidad de O’Higgins. (2026). Planificación de curso '
        'COM50100 Aprendizaje Reforzado. Sección V, Bibliografía y recursos obligatorios.')
    # [5] va después de la referencia al código.
    ref._p.getparent().remove(ref._p);original[64]._p.addnext(ref._p)
    ref.paragraph_format.space_after=Pt(4)
    for r in ref.runs:r.font.size=Pt(10)
    for p in original[61:65]:
        for r in p.runs:r.font.size=Pt(10)
    toc=json.loads(args.toc_json.read_text()) if args.toc_json else {
        'Resumen':2,'Estado del arte':2,'Metodología':3,'Resultados':6,
        'Discusión':9,'Conclusión':9,'Referencias':9}
    for p,name in zip(original[13:20],toc):
        p.text=name+'\t'+str(toc[name])
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.6),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
    for root in (doc.styles.element,doc._element):
        for border in list(root.iter(qn('w:pBdr'))):border.getparent().remove(border)
    path=ROOT/'docs/Informe_Final_Digimon_RPG_v019.docx';doc.save(path)
    evidence={'release':'0.19','experiment':'v0.11','checkpoint_max':20000,'n_seeds':5,
        'play_policy_mc_episodes':60000,'reachable_nonterminal_states':48553,'software_tests':161,
        'windows_native':'pending','repository_public_url':None,
        'figure_x_axis':'linear episode count','report_toc_pages':toc,
        'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (ROOT/'resultados/convergencia_v011/resumen_v011.json',
                             ROOT/'resultados/convergencia_v011/curvas_resumen.csv',
                             ROOT/'resultados/validacion_v0_9.json',ROOT/'politicas/dp.json',ROOT/'politicas/mc.json')},
        'course_sources':['Final_Project.pdf','Catedra_13_Monte_Carlo_Methods_III.pdf',
                          '202608202205_3DE23E_20178023__Syllabus_Aprendizaje_Reforzado(1).pdf']}
    (ROOT/'resultados/evidencia_informe_v019.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    # Fuente de lectura en texto; las ecuaciones nativas se identifican en el DOCX.
    output=[]
    from docx.table import Table
    for element in doc.element.body:
        if element.tag==qn('w:p'):
            p=Paragraph(element,doc)
            if p.text:output.append(('## ' if p.style.name.startswith('Heading') else '')+p.text)
            elif element.xpath('.//m:oMath'):
                output.append('Ecuación nativa Word: '+''.join(element.xpath('.//m:t/text()')))
        elif element.tag==qn('w:tbl'):
            t=Table(element,doc)
            output.append('\n'.join(' | '.join(c.text.replace('\n',' ') for c in row.cells) for row in t.rows))
    (ROOT/'docs/Informe_Final_Digimon_RPG_v019.md').write_text('\n\n'.join(output),encoding='utf-8')
    print(path)


if __name__=='__main__':main()
