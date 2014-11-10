# -*- coding: utf-8 -*-

"""Skript na TeXovanie vypoctov ktore sa nechce nikomu pisati
    Author: Stanislav Parnicky
    Usage: import tx and save_pdf to file with homework     
        use tx(TeXsourcecode) to append to buffer and save_pdf(filename) to save it to file in cwd
"""

tex_start = '''\\documentclass[8pt, oneside]{extarticle}         
\\usepackage[a4paper, margin=1in]{geometry}                     
\\usepackage[slovak]{babel}
\\usepackage[IL2]{fontenc}
\\usepackage[utf8]{inputenc}
\\geometry{a4paper}                              
%%\\geometry{landscape}                          
%%\\usepackage[parfill]{parskip}                
%%\\usepackage{graphicx}                       
                                             
\\usepackage{amssymb}
\\usepackage{amsmath}
\\usepackage{fancyhdr}

\\title{%s}
\\author{Stanislav Párnický}
\\date{}                                    

\\makeatletter
\\let\\runauthor\\@author
\\let\\runtitle\\@title
\\makeatother
\\pagestyle{fancy}
\\fancyhf{}
\\rhead{\\runauthor}
\\lhead{\\runtitle{} (page \\thepage)}
%%\\rfoot{Page \\thepage}


\\expandafter\\def\\expandafter\\normalsize\\expandafter{%%
    \\normalsize
    \\setlength\\abovedisplayskip{2pt}
    \\setlength\\belowdisplayskip{2pt}
    \\setlength\\abovedisplayshortskip{1pt}
    \\setlength\\belowdisplayshortskip{1pt}
}
\\newenvironment{polynomial}
  {\\par\\vspace{\\abovedisplayskip}%%
   \\setlength{\\leftskip}{\\parindent}%%
   \\setlength{\\rightskip}{\\leftskip}%%
   \\medmuskip=3mu plus 2mu minus 2mu
   \\binoppenalty=0
   \\noindent$\\displaystyle}
  {$\\par\\vspace{\\belowdisplayskip}}
\\begin{document}
%%\\maketitle
'''

tex_end = "\\end{document}"


def generate_pdf(pdfname,title,tex):
    """
    Genertates the pdf from string
    """
    import subprocess
    import os
    import tempfile
    import shutil

    current = os.getcwd()
    temp = tempfile.mkdtemp()
    os.chdir(temp)

    f = open('vzorce.tex','w')
    f.write(tex_start % title)
    f.write(tex)
    f.write(tex_end)
    f.close()

    proc=subprocess.Popen(['pdflatex','vzorce.tex'])
    proc.communicate()
       

    os.rename('vzorce.pdf', pdfname) 
    shutil.copy(pdfname,current)
    os.rename('vzorce.tex', pdfname+'.tex') 
    shutil.copy(pdfname+'.tex',current)
    shutil.rmtree(temp)
    os.chdir(current)

out = []
def tx(tex):
    """Vstupna funkcia ktora vklada do buffera"""
    out.append(tex)


def save_pdf(pdfname, title="Domáca úloha"):
    """Ulozi pdf z texu do suboru pdfname"""
    tex = "\n\n".join(out)
    generate_pdf(pdfname,title,tex)
