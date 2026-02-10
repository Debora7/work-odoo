from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

import json

import uno
import os
import sys
import tempfile
import shutil
from urllib.request import pathname2url
from com.sun.star.beans import PropertyValue

import atexit
import logging

url_map = Map([
    Rule('/convert-word-to-pdf', endpoint='convert_word_to_pdf', methods=['POST']),
    Rule('/xls-formulas-to-data', endpoint='xls_formula_to_data', methods=['POST']),
])

@atexit.register
def application(environ, start_response):
    request = Request(environ)

    urls = url_map.bind_to_environ(environ)

    try:
        endpoint, args = urls.match()
    except Exception as e:
        logging.info(e)
        start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
        return [str(e).encode('utf-8')]

    if endpoint == 'convert_word_to_pdf':
         status, headers, body = convert_word_to_pdf(request)
    elif endpoint == 'xls_formula_to_data':
        status, headers, body = xls_formula_to_data(request)
    else:
        start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
        return [b'No endpoint implemented']

    start_response(status, headers)
    return [body]

def convert_word_to_pdf(request: Request):
    try:
        # Get word from request
        file = request.files.get('file')
        if not file:
            # 404 Not Found
            return ('400 BAD REQUEST', [('Content-Type', 'text/plain')], b'No file provided')

        data = file.read()

        # Convert word to pdf in libreoffice headless
        pdf_bytes = pdf_converter(data)

        # Return the pdf
        return ('200 OK', [('Content-Type', 'application/pdf')], str({'response' : pdf_bytes}).encode())

    except Exception as e:
        return ('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/plain')], str(e).encode('utf-8'))

def to_lo_url(path: str) -> str:
    abs_path = os.path.abspath(path)
    return uno.systemPathToFileUrl(abs_path)

def pdf_converter(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
        tmp_in.write(file_bytes)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path.replace(".docx", ".pdf")

    input_url = to_lo_url(tmp_in_path)
    output_url = to_lo_url(tmp_out_path)

    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )

    ctx = resolver.resolve(
        "uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext"
    )

    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )

    props = (
        PropertyValue(Name="Hidden", Value=True),
        PropertyValue(Name="FilterName", Value="MS Word 2007 XML")
    )
    doc = desktop.loadComponentFromURL(input_url, "_blank", 0, props)

    pdf_props = (
        PropertyValue(Name="FilterName", Value="writer_pdf_Export"),
    )

    doc.storeToURL(output_url, pdf_props)
    doc.close(True)

    with open(tmp_out_path, "rb") as f:
        pdf_bytes = f.read()

    os.remove(tmp_in_path)
    os.remove(tmp_out_path)

    return pdf_bytes

def xls_formula_to_data(request: Request):
    try:
        # Get xls from request
        data = request.files.get('file')
        if not data:
            return ('400 BAD REQUEST', [('Content-Type', 'text/plain')], b'No file provided')

        xls_bytes = data.read()

        # Calculate data from xls in libreoffice headless
        calculated_bytes = recalc_xls(xls_bytes)

        # Return the xls calculated
        return ('200 OK', [('Content-Type', 'application/vnd.ms-excel')], str({'response' : calculated_bytes}).encode())

    except Exception as e:
        logging.info(e)
        return ('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/plain')], str(e).encode('utf-8'))

def recalc_xls(file_bytes):
    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    tmp_in.write(file_bytes)
    tmp_in.close()  # Important: close so LibreOffice can open it
    tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path.replace(".xlsx", "_out.xlsx")  # output file

    input_url = to_lo_url(tmp_in_path)
    output_url = to_lo_url(tmp_out_path)

    # Connect to LibreOffice
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    ctx = resolver.resolve(
        "uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext"
    )
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )

    props = (PropertyValue(Name="Hidden", Value=True),)
    doc = desktop.loadComponentFromURL(input_url, "_blank", 0, props)

    save_props = (PropertyValue(Name="FilterName", Value="Calc MS Excel 2007 XML"),)
    doc.storeToURL(output_url, save_props)
    doc.close(True)

    # Read the output
    with open(tmp_out_path, "rb") as f:
        out_bytes = f.read()

    # Clean up
    os.remove(tmp_in_path)
    os.remove(tmp_out_path)

    return out_bytes

if __name__ == '__main__':
    run_simple('0.0.0.0', 8084, application)
