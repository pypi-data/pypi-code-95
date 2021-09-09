# Control import of slides from pdf to svg-editable format.
# inkscape -z -f "Input.pdf" -l "Output.svg"
# https://github.com/eea/odfpy
import os
import shutil
from jinjafy import jinjafy_comment
from bs4 import BeautifulSoup
import glob
from jinjafy import execute_command
import zipfile
import tempfile

CDIR = os.path.dirname(os.path.realpath(__file__))
CDIR = CDIR.replace('\\','/')

SVG_EDIT_RELPATH = "osvgs" # files that are supposed to be edited goes here.
SVG_TMP_RELPATH = "tmp" # various files that can be flat out deleted goes here
SVG_TEXINCLUDE_RELPATH = "do_not_edit" # the no_fonts version and the pure (+fonts) versions goes here
DTU_beamer_base = CDIR +"/DTU_Beamer_files"
BLANK_PNG =DTU_beamer_base + "/blank.png"

def ensure_dir(dname):
    assert False
    if not os.path.exists(dname):
        os.mkdir(dname)

def join_pdfs(slide_deck_pdf, outfile):
    assert False
    dn = os.path.dirname(slide_deck_pdf[0])
    files = [os.path.relpath(os.path.dirname(pdf), start=dn) + "/" + os.path.basename(pdf) for pdf in slide_deck_pdf]
    outf = os.path.relpath(os.path.dirname(outfile), start=dn) + "/" + os.path.basename(outfile)
    cmd = "cd " + dn + " && pdftk " + " ".join(files) + " cat output " + outf
    execute_command(cmd.split())


def li_import(slide_deck_pdf, tex_output_path=None, num_to_take=None, force=False, svg_pfix="osvg", svg_height=743.75, svg_width=992.5,
              svg_converted_slides="svg_converted_slides.tex"):
    assert False
    '''
    svg_height and svg_width are used to scale the converted image. This is useful because otherwise the viewbox
    will fail to match the DTU template. I.e. these numbers will generally change dependent on the LaTeX template.

    :param slide_deck_pdf:
    :param tex_output_path:
    :param num_to_take:
    :param force:
    :param svg_pfix:
    :param svg_height:
    :param svg_width:
    :return:
    '''
    # take this slide deck. Generate beamer, svg output.

    if isinstance(slide_deck_pdf, list):
        dn = os.path.dirname(slide_deck_pdf[0])
        ofile = os.path.join(dn, "tmp.pdf")
        join_pdfs(slide_deck_pdf, ofile)
        slide_deck_pdf = ofile

    if tex_output_path is None:
        tex_output_path = slide_deck_pdf[:-4]+"_output.tex"

    output_dir = os.path.dirname(tex_output_path)

    # if output_dir is None:
    #     output_dir = os.path.dirname(slide_deck_pdf)
    assert(os.path.exists(output_dir))
    svg_tmp_dir = output_dir + "/" + SVG_EDIT_RELPATH +"/" + SVG_TMP_RELPATH
    svg_texinclude_dir = output_dir + "/" + SVG_EDIT_RELPATH +"/" +SVG_TEXINCLUDE_RELPATH
    svg_edit_dir = output_dir + "/" +SVG_EDIT_RELPATH
    tex_output_file = os.path.basename(tex_output_path)

    print("Converting slides to output: " + tex_output_file)
    if os.path.exists(output_dir + "/" + tex_output_file) or glob.glob(svg_edit_dir + "/*.svg"):
        print("Non-empty output directory...")
        if not force:
            raise Exception("Non-empty output directory. Please clean")

    ensure_dir(svg_edit_dir)
    ensure_dir(svg_tmp_dir)
    ensure_dir(svg_texinclude_dir)

    if not output_dir:
        raise Exception("Must specify output directory!")

    lecture_tex_out = move_template_files(output_dir, tex_output_file)
    osvgs_basename = []
    print("Splitting slide deck into images...")

    # slide_deck_split_svg = slidedeck_to_images(slide_deck_pdf, svg_tmp_dir + "/" + svg_pfix + "-%i.svg",
    #                                            num_to_take=num_to_take)
    slide_deck_split_svg = slidedeck_to_images(slide_deck_pdf, svg_tmp_dir+"/"+svg_pfix+"-%i.svg", num_to_take=num_to_take)
    print("Converting svg to osvg..")
    for i,osvg in enumerate(slide_deck_split_svg):
        dosvg = raw_svg_to_osvg(osvg, overwrite_existing=True, height=svg_height, width=svg_width)
        osvgs_basename.append(dosvg)

    print("jinjafying and cleaning...")
    # osvgs_basename = osvgs_basename[3:] # Drop first 3 slides; automatically generated.
    data = {'osvgs_basename' : osvgs_basename}
    s = jinjafy_comment(data, jinja_tag="jinja1")
    with open(output_dir + "/%s"%svg_converted_slides, 'w') as f:
        f.write(s)
    return lecture_tex_out

# <jinja1>
# {% for sf in osvgs_basename %}
# \begin{frame}\osvg{{"{"}}{{sf}}{{"}"}}
# % add content here
# \end{frame}
# {% endfor %}
# </jinja1>
# \begin{textblock}{1}(0,0)
# 	\includesvg[width=1.0\linewidth]{{"{"}}{{sf}}{{"}"}}
# \end{textblock}\overlabel{ {{sf}} }
# SVG editable file (i.e. with background image) to file which can be imported into
# the .tex file.

'''
Take a raw svg in the tmp directory and compile it into the nice svg format with empty, white background.
This can be used when importing a new slide deck or when inserting a new overlabel tag somewhere in a
tex document.
'''
def raw_svg_to_osvg(raw_svg_file, overwrite_existing=False, height=None, width=None):
    svg_tmp_dir = os.path.dirname(raw_svg_file)
    svg_edit_dir = os.path.dirname(svg_tmp_dir)
    ofile_edit = svg_edit_dir + "/" + os.path.basename(raw_svg_file)
    # if height is not None and width is not None:
    #     svg_set_hw_(raw_svg_file, raw_svg_file,height=height, width=width)

    ofile_fonts_pure = rm_svg_bg(svg_input=raw_svg_file, svg_output=ofile_edit, height=height, width=width)
    png_file = svg_tmp_dir + "/" + os.path.basename(ofile_fonts_pure)[:-4] + ".png"
    shutil.copyfile(BLANK_PNG, png_file)
    ofile_edit = add_png_background_to_svg(svg_input=ofile_fonts_pure, svg_output=None, png_file=png_file)
    pdf_nofonts, svg_fonts = svg_edit_to_importable(ofile_edit)
    osvgs_basename = os.path.basename(raw_svg_file)[:-4]
    return osvgs_basename


'''
Related to li_import. 
Set the width/height of an imported slide svg image in case it does not match the DTU template. 
'''
def svg_set_hw_(svg_in, svg_out, height, width):
    assert False
    print(f"HW fix [{height} {width}] > {svg_in} -> {svg_out}")

    with open(svg_in, 'r', encoding="UTF-8") as f:
        soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")
        tags = soup.find_all("svg")
        assert (len(tags) == 1)
        tag = tags[0]
        tag['height'] = str(height)
        tag['width'] = str(width)
        tag['viewBox'] = f"0 0 {height} {width}"
    # print([svg_input, logo_rem, bg_rem, tx_rem])
    with open(svg_out, 'bw') as f:
        f.write(soup.encode("UTF-8"))
    return
    with open(svg_in, 'r', encoding="UTF-8", errors="surrogateescape") as f:
        soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")
        tags = soup.find_all("svg")
        assert(len(tags) == 1)
        tag = tags[0]
        tag['height'] = str(height)
        tag['width'] = str(width)
        tag['viewBox'] = f"0 0 {height} {width}"
        s2 = soup.__copy__()
        # sout = s2.encode("UTF-8")
    # f.close()
    with open(svg_out, 'w', encoding="UTF-8") as f2:
        f2.write(str(s2))

def svg_check_background_layer(svg_edit_file, verbose=False):
    assert False

    # Check if svg background layer is pointing to the right .png file.
    # this may not be the case sometimes because svg files are moved, etc. which overwrite the default
    # background .png path.
    with open(svg_edit_file, 'r', encoding="UTF-8",errors="surrogateescape") as f:
        soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")
        g = None
        for i in soup.findAll("g", {'inkscape:groupmode': 'layer'}):
            if i['inkscape:label'] == "bg_layer":
                g = i
                break
        ok = True
        bgim = g.find("image")
        bg_png = bgim['xlink:href']
        real_png = os.path.dirname(svg_edit_file) + "/" + SVG_TMP_RELPATH + "/" + os.path.basename(svg_edit_file)[:-4] + ".png"
        real_png = os.path.relpath(real_png, start=os.path.dirname( svg_edit_file) )
        bg_png = os.path.relpath(bg_png,start=os.path.dirname( svg_edit_file)  )
        if real_png != bg_png:
            print("slider:warning> Bungled background png image in " + svg_edit_file)
            s = jinjafy_comment({'png_file': real_png}, jinja_tag="jinja3")
            new_img = BeautifulSoup(s, "html.parser")
            g.insert_after( new_img)
            g.unwrap()
            bgim.unwrap()

            with open(svg_edit_file[:-4]+"_test.svg", "w") as f2:
                f2.write(soup.prettify(formatter="xml"))

# <jinja3>
# <g inkscape:groupmode="layer" id="layer1" inkscape:label="bg_layer" style="display:inline" sodipodi:insensitive="true">
#      <image
#        xlink:href="{{png_file}}"
#        width="100%"
#        height="100%"
#        preserveAspectRatio="none"
#        style="image-rendering:optimizeQuality"
#        id="image4444th"
#        x="0"
#        y="0" />
#  </g>
# </jinja3>



def svg_edit_to_importable(svg_edit_file,verbose=False):
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

            from slider.convert import svg2pdf
            svg2pdf(svg_fonts_layers[-1], fout=pdf_nofonts_layers[-1], crop=False, text_to_path=True, export_area_page=True)
            # cmd = ['inkscape', '-C', '-T', '--without-gui', '--file=%s'%svg_fonts_layers[-1], '--export-pdf=%s' % pdf_nofonts_layers[-1]]

    if verbose:
        print("svg_edit_to_importable called. converted svg file\n  > %s\nto files:"%svg_edit_file)
        for s in pdf_nofonts_layers + svg_fonts_layers:
            print("  > " + s)

    return pdf_nofonts_layers, svg_fonts_layers

# <jinja2>
# {{svg_start}}
# <g inkscape:groupmode="layer" id="layer1" inkscape:label="bg_layer" style="display:inline" sodipodi:insensitive="true">
#      <image
#        xlink:href="{{png_file}}"
#        width="100%"
#        height="100%"
#        preserveAspectRatio="none"
#        style="image-rendering:optimizeQuality"
#        id="image4444th"
#        x="0"
#        y="0" />
#  </g>
# <g inkscape:groupmode="layer"
#     id="layer2"
#     inkscape:label="Layer 1"
#     style="display:inline">
# {{svg_end}}
# </g></svg>
# </jinja2>
def add_png_background_to_svg(svg_input, png_file, svg_output=None):
    if not svg_output: svg_output = svg_input
    rp = os.path.relpath(png_file, os.path.commonprefix([svg_output, png_file]))
    rp = rp.replace("\\", "/")

    with open(svg_input,'r', encoding="UTF-8") as f:
        svg = f.read()
    mds = "</metadata>"
    mds_id = svg.find(mds)
    if mds_id < 0:
        # file has no meta data.
        j = svg.find(">", svg.find("<svg"))
        svg = svg[:j+1] + "<metadata></metadata>" +svg[j+1:]
        mds_id = svg.find(mds)

    mds_dex = mds_id+len(mds)

    data = {'png_file' : rp, 'svg_start': svg[:mds_dex],'svg_end': svg[mds_dex:]}
    svg = jinjafy_comment(data, jinja_tag="jinja2")

    si = svg.find("<svg") + 4
    dsvg = ' xmlns:sodipodi = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"\n xmlns:inkscape = "http://www.inkscape.org/namespaces/inkscape" \n'
    svg = svg[:si] + dsvg + svg[si:]

    with open(svg_output, 'w',encoding="UTF-8") as f:
        f.write(svg)
    return svg_output


def slidedeck_to_images(slide_deck_pdf, base_out_pattern, num_to_take=None):
    assert False
    if not os.path.exists(os.path.dirname(base_out_pattern)):
        os.mkdir(os.path.dirname(base_out_pattern))
    num_pages = num_pages_in_pdf(slide_deck_pdf)
    opat = base_out_pattern[:-4] + "_tmp.pdf"
    opat.replace("%i", '%d')
    cmd = f"pdftk {slide_deck_pdf} burst output {opat} compress"
    print("pdftk splitting into ", num_pages)

    execute_command(cmd.split())
    outfiles = []
    slide_deck_split_pdf = [base_out_pattern[:-4] % (i + 1) + "_tmp.pdf" for i in range(num_pages)]
    for i, opdf in enumerate(slide_deck_split_pdf):
        print("convertion", i, opdf)
        ofile = base_out_pattern %(i+1)
        cmd = f"pdf2svg {opdf} {ofile}"
        execute_command(cmd.split())
        b = os.path.getsize(ofile)
        # print(b)
        if b == 0:
            print("Skipping this file because it has size 0...")
        else:
            outfiles.append(ofile)

    return outfiles

def slidedeck_to_images_DEFUNCT(slide_deck_pdf, base_out_pattern, num_to_take=None):
    assert False
    if not os.path.exists(os.path.dirname(base_out_pattern)):
        os.mkdir(os.path.dirname(base_out_pattern))

    num_pages = num_pages_in_pdf(slide_deck_pdf)
    slide_deck_split_pdf = [base_out_pattern[:-4] % (i + 1) + "_tmp.pdf" for i in range(num_pages)]
    if num_to_take: slide_deck_split_pdf = slide_deck_split_pdf[0:num_to_take]

    outfiles = []
    for i, opdf in enumerate(slide_deck_split_pdf):
        print("convertion", i, opdf)
        ofile = base_out_pattern %(i+1)
        slide_to_image(slide_deck_pdf, ofile, page_to_take=i+1)
        outfiles.append(ofile)
    return outfiles

def num_pages_in_pdf(pdf_file):
    assert False
    cmd = ['pdftk', '%s' % pdf_file, 'dump_data']
    ss = execute_command(cmd)[0].splitlines()
    s = int([s for s in ss if 'NumberOfPages' in s].pop().split()[-1])
    return s


def slide_to_image(slide_deck_pdf, output, page_to_take=1, use_inkscape=True):
    if not os.path.exists(os.path.dirname(output)):
        os.mkdir(os.path.dirname(output))
    slide_deck_split_pdf = output[:-4] + "_tmp.pdf"
    ext = output[-3:]
    if ext == "svg":
        from slider.convert import pdf2svg
        pdf2svg(slide_deck_pdf, fout=output, page_no=page_to_take)
        # cmd = ['pdftk', '%s' % slide_deck_pdf, 'cat', '%i' % page_to_take, 'output', '%s' % slide_deck_split_pdf]
        # # page_to_take = 1

        # if use_inkscape:
        #     cmd = ['inkscape', '-C', '--without-gui', '--file=%s' % slide_deck_split_pdf, '-l', '%s' % output]
        # else:
        #     cmd = ['pdf2svg', slide_deck_split_pdf, output]
    else:
        if os.path.exists(output):
            os.remove(output)
        cmd = ("pdftocairo -png -f %i -l %i"% (page_to_take, page_to_take)).split(" ") + [slide_deck_pdf, output]
        execute_command(cmd)
    if ext == "png":
        png_with_postfix = glob.glob(output + "-*.png")
        if not png_with_postfix:
            print("WARNING! no png generated.")
            print(output)
        else:
            png_with_postfix = png_with_postfix.pop()
            shutil.move(png_with_postfix, output)

    return output


def move_template_files(output_dir="examples/output", output_tex_file=None):
    files_to_move = ["tex_dtu_logo.pdf", "tex_dtu_compute_a_uk.pdf", "tex_dtu_frise.pdf", "dtucolours.tex",
                     "beamerthemeDTU.sty", "beamerfontthemeDTU.sty","beamercolorthemeDTU.sty",
                     "beamerinnerthemeDTU.sty", "beamerouterthemeDTU.sty", "departments.tex", "tex_compute_uk.pdf",
                     "02450_beamer_preamble.tex",  # Deprecated.
                     'beamer_slider_preamble.tex', # The current version.
                     ]

    zipf = DTU_beamer_base + "/DTU_Beamer_files.zip"
    # os.path.exists(zipf)

    tmp = tempfile.mkdtemp()

    # output_dir = output_dir)
    # import random
    # "".join( [str(random.randint(1, 10))  for _ in range(10)] )
    # tmp = str(output_dir) +   "/"+  "".join( [str(random.randint(1, 10))  for _ in range(10)] )
    # os.mkdir(tmp)

    with zipfile.ZipFile(zipf) as zip:
        # for files in zip.namelist():
        #     data = zip.read(files, output_dir)
        #     myfile_path = output_dir / Path(files).name
        #     myfile_path.write_bytes(data)
        # zip.extract(name, output_dir +"/" + os.path.basename(name))
        zip.extractall(tmp)

    for f in glob.glob(tmp + "/**/*.*"):
        shutil.move(f, str(output_dir) + "/"+os.path.basename(f))
    shutil.rmtree(tmp)
    if output_tex_file != None:
        assert False
    return
    print(f)

    sd = list( zip(files_to_move, files_to_move) )
    if output_tex_file:
        sd.append( ("02450_lectures_base.tex", output_tex_file))
    for (source,dest) in sd:
        shutil.copy(DTU_beamer_base + "/" + source, output_dir + "/" + dest)

    if output_tex_file:
        lecture_tex_out = output_dir + "/" + output_tex_file
    else:
        lecture_tex_out = None

    return lecture_tex_out


def rm_svg_bg(svg_input, svg_output=None, fix_bg=True, fix_txt=True, fix_logo=True, height=None, width=None):
    logo_rem = 0
    tx_rem = 0
    bg_rem = 0
    if not svg_output:
        svg_output = svg_input

    with open(svg_input, 'r', encoding="UTF-8") as f:
        soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")
        BG_white = ["fill:#ffffff;fill-opacity:1;fill-rule:nonzero;stroke:none", "fill:#ffffff;fill-opacity:1;fill-rule:evenodd;stroke:none"]
        for bgw in BG_white:
            gg = soup.findAll("path", {"style" : bgw})
            for g in gg:
                if not fix_bg: break
                g['style'] = bgw.replace("opacity:1", "opacity:0")
                bg_rem += 1
                if bg_rem >= 2: break

        dtulogo = soup.findAll("image")
        for i in dtulogo:
            if "iVBORw0KGgoAAAANSUhEUgAABawAAAFcCAYAAAAkg" in i['xlink:href'] and fix_logo:
                i.extract()
                logo_rem += 1

        btx = ["font-variant:normal;font-weight:bold;font-size:8px;font-family:Verdana;-inkscape-font-specification:Verdana-Bold;writing-mode:lr-tb;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none",
               "font-variant:normal;font-weight:normal;font-size:9px;font-family:Verdana;-inkscape-font-specification:Verdana;writing-mode:lr-tb;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none",
               "font-variant:normal;font-weight:bold;font-size:9px;font-family:Verdana;-inkscape-font-specification:Verdana-Bold;writing-mode:lr-tb;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none",
               "font-variant:normal;font-weight:bold;font-size:8px;font-family:Arial;-inkscape-font-specification:Arial-BoldMT;writing-mode:lr-tb;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none",
               "font-variant:normal;font-weight:normal;font-size:9px;font-family:Arial;-inkscape-font-specification:ArialMT;writing-mode:lr-tb;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none"]

        for j,style in enumerate(btx):
            if not fix_txt:
                break
            for tx in soup.findAll("text", {"style": style}):
                tx.extract()
                tx_rem += 1

        # soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")
        if height is not None and width is not None:
            ''' 
            We are doing this if the svg is being imported and the height/width might not match the DTU template viewbox. 
                        
            '''
            tags = soup.find_all("svg")
            if len(tags) != 1:
                a = 1234

            assert (len(tags) == 1)
            tag = tags[0]
            tag['height'] = str(height)
            tag['width'] = str(width)
            tag['viewBox'] = f"0 0 {height} {width}"


    print([svg_input, logo_rem, bg_rem, tx_rem])
    with open(svg_output, 'bw') as f:
        f.write(soup.encode("UTF-8"))
    return svg_output


if __name__ == "__main__":
    print("operating...")
    lecture_tex_out = li_import("examples/ex1/Lecture11.pdf", output_dir="examples/output", num_to_take=3)
    print("Wrote new main file: " + lecture_tex_out)