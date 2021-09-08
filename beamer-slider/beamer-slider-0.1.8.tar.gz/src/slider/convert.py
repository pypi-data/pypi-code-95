from jinjafy import execute_command
import os
from bs4 import BeautifulSoup

def svg2pdf(fin, fout=None, crop=True, text_to_path=False, export_area_page=True):
    """
     -C, --export-area-page                     Area to export is page
       -T, --export-text-to-path                  Convert text to paths (PS/EPS/PDF/SVG)
    """
    # text_to_path = True
    if fout is None:
        fout = fin[:-4] + ".pdf"
    cmd = ['inkscape']
    if export_area_page:
        cmd.append("-C")
    if text_to_path: # Good idea for inkscape which seems to bungle the fonts (space in font names?)
        cmd.append("-T")
    cmd.append(fin)
    cmd.append(f"--export-filename={fout}")
    # '-C', '--without-gui', f'--file={fin}', f'--export-pdf={fout}']
    # cmd = ['inkscape', '-C', '-T', '--without-gui', '--file=%s'%svg_fonts_layers[-1], '--export-pdf=%s' % pdf_nofonts_layers[-1]]
    execute_command(cmd)
    # cmd = f"pdftocairo {fout} -pdf {fout}"
    # execute_command(cmd.split())

    if crop:
        cmd = ['pdfcrop', fout, fout]
        execute_command(cmd)



def pdf2svg(fin, fout, page_no=None):
    '''
    To remove fonts look at
    https://tex.stackexchange.com/questions/23407/how-can-i-convert-text-to-paths-with-pdflatex
    convert to ps and back to pdf
    '''
    if fout is None:
        fout = fin[:-4] + ".svg"

    '''
    pdftocairo -svg C:/Users/tuhe/Documents/02465public/Lectures/Lecture_2/Latex/Lecture_2_NO_SVGS.pdf C:/Users/tuhe/Documents/02465public/Lectures/Lecture_2/Latex/osvgs/tmp/determpath.svg -f 2 -l 2
    
    '''
    cmd = ['pdftocairo', '-svg', fin, fout]
    if page_no is not None:
        if not isinstance(page_no, str):
            page_no = str(page_no)
        cmd += ['-f', str(page_no), '-l', str(page_no)]

    execute_command(cmd)


def pdf2png(fin, fout=None, scale_to=None):
    if fout is None:
        fout = fin[:-4] + ".png"
    fout = fout[:-4]
    cmd = f"pdftocairo -png -singlefile {fin} {fout}"
    if scale_to is not None:
        cmd += f" -scale-to {scale_to}"
    execute_command(cmd.split())
    return fout + ".png"


def pdfcrop(fin, fout=None):
    if fout is None:
        fout = fin
    cmd = f"pdfcrop {fin} {fout}"
    execute_command(cmd.split())



def svg_edit_to_importable(svg_edit_file,verbose=False, keep_background_layer=True):
    assert False
    """
    Take an inkscape file as input and split it into layers.
    CODE NOT IN USE RIGHT NOW; MUST WORK OUT WHAT TO USE IT FOR.
    """
    odir = os.path.dirname(svg_edit_file)
    fn = os.path.basename(svg_edit_file)[:-4]

    pdf_nofonts_base = odir + "/x_do_not_edit_%s-l%s_nofonts.pdf"
    svg_fonts_base =  odir + "/" + SVG_TEXINCLUDE_RELPATH + "/%s-l%s_fonts.svg"
    if not os.path.exists(os.path.dirname(svg_fonts_base)):
        os.mkdir(os.path.dirname(svg_fonts_base))

    pdf_nofonts_layers = []
    svg_fonts_layers = []

    with open(svg_edit_file, 'r', encoding="UTF-8",errors="surrogateescape") as f:
        soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")
        for i in soup.findAll("image", {'id': 'image4444th'}):
            i.extract()

        layer_labels = []
        for i in soup.findAll("g", {'inkscape:groupmode': 'layer'}):
            if i['inkscape:label'] == "bg_layer":
                #i.extract()
                pass
            else:
                layer_labels.append(i['inkscape:label'])

        for j in range(len(layer_labels)):
            s2 = soup.__copy__()
            for i in s2.findAll("g", {'inkscape:groupmode': 'layer'}):
                if layer_labels[j] == i['inkscape:label'] or i['inkscape:label'] == "bg_layer":
                    pass
                else:
                    i.extract()
            # now you got an image only with this layer. save it.
            layer_number = layer_labels[j].split(" ").pop()
            pdf_nofonts_layers.append(pdf_nofonts_base%(fn,layer_number))
            svg_fonts_layers.append(svg_fonts_base % (fn, layer_number))

            with open(svg_fonts_layers[-1], 'bw') as f2:
                f2.write(s2.encode("UTF-8"))

            cmd = ['inkscape', '-C', '-T', '--without-gui', '--file=%s'%svg_fonts_layers[-1], '--export-pdf=%s' % pdf_nofonts_layers[-1]]
            execute_command(cmd)

    if verbose:
        print("svg_edit_to_importable called. Converting svg file\n  > %s\nto files:"%svg_edit_file)
        for s in pdf_nofonts_layers + svg_fonts_layers:
            print("  > " + s)

    return pdf_nofonts_layers, svg_fonts_layers
