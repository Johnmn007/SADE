from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
import os
import pdfkit
from datetime import datetime
import tempfile
import platform
import io
from . import reportes_bp
from app.services.report_generator import ReportGenerator
from app.models import Reporte, Estudiante
from app.extensions import db


def get_pdf_config():
    """Configuración portable y compatible con Render."""
    try:
        if platform.system() == "Windows":
            possible_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                'wkhtmltopdf.exe'
            ]
        else:
            possible_paths = [
                '/usr/bin/wkhtmltopdf',
                '/usr/local/bin/wkhtmltopdf',
                'wkhtmltopdf'
            ]

        for path in possible_paths:
            if os.path.exists(path):
                return pdfkit.configuration(wkhtmltopdf=path)

        return pdfkit.configuration()

    except Exception as e:
        print(f"[WARN] Error configurando wkhtmltopdf: {e}")
        return pdfkit.configuration()


# ======================================
# PANEL PRINCIPAL
# ======================================

@reportes_bp.route('/')
@login_required
def index():
    return render_template('reportes/index.html')


# ======================================
# REPORTE INDIVIDUAL
# ======================================

@reportes_bp.route('/individual')
@login_required
def individual():
    estudiantes = Estudiante.query.filter_by(activo=True).all()
    return render_template('reportes/individual.html', estudiantes=estudiantes)


@reportes_bp.route('/generar-individual', methods=['POST'])
@login_required
def generar_individual():
    try:
        estudiante_id = request.form.get('estudiante_id')
        semestre = request.form.get('semestre')
        formato = request.form.get('formato', 'html')

        generator = ReportGenerator()
        resultado = generator.generar_reporte_riesgo_individual(estudiante_id, semestre)

        html = resultado["html"]

        # Guardar registro en BD (SOLO HTML)
        reporte = Reporte(
            tipo_reporte='INDIVIDUAL_RIESGO',
            titulo=f'Reporte de Riesgo - {resultado["estudiante"].nombres} {resultado["estudiante"].apellidos}',
            descripcion=f'Reporte individual de riesgo académico para el semestre {semestre}',
            parametros={"estudiante_id": estudiante_id, "semestre": semestre},
            contenido=html,
            usuario_id=current_user.id
        )
        db.session.add(reporte)
        db.session.commit()

        # ---------------------------------------
        # GENERAR PDF
        # ---------------------------------------
        if formato == 'pdf':
            try:
                config = get_pdf_config()

                options = {
                    'page-size': 'A4',
                    'margin-top': '0.5in',
                    'margin-right': '0.5in',
                    'margin-bottom': '0.5in',
                    'margin-left': '0.5in',
                    'encoding': 'UTF-8',
                    'enable-local-file-access': ''
                }

                # GENERAR PDF EN MEMORIA (NO EN DISCO)
                pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)

                return send_file(
                    io.BytesIO(pdf_bytes),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=f"reporte_individual_{estudiante_id}.pdf"
                )

            except Exception as err:
                flash(f"Error generando PDF: {err}", "danger")

        # Fallback: mostrar HTML
        return render_template('reportes/vista_previa.html', contenido=html, titulo=reporte.titulo)

    except Exception as e:
        db.session.rollback()
        flash(f"Error generando reporte: {e}", "danger")
        return redirect(url_for('reportes.individual'))


# ======================================
# REPORTE GENERAL
# ======================================

@reportes_bp.route('/general')
@login_required
def general():
    return render_template('reportes/general.html')


@reportes_bp.route('/generar-general', methods=['POST'])
@login_required
def generar_general():
    try:
        semestre = request.form.get('semestre')
        categoria_filtro = request.form.get('categoria_filtro')
        formato = request.form.get('formato', 'html')

        generator = ReportGenerator()
        resultado = generator.generar_reporte_riesgo_general(semestre, categoria_filtro)

        html = resultado["html"]

        reporte = Reporte(
            tipo_reporte='GENERAL_RIESGO',
            titulo=f'Reporte General de Riesgo - {semestre}',
            descripcion=f'Reporte general de riesgo académico. Filtro: {categoria_filtro}',
            parametros={"semestre": semestre, "categoria_filtro": categoria_filtro},
            contenido=html,
            usuario_id=current_user.id
        )
        db.session.add(reporte)
        db.session.commit()

        if formato == "pdf":
            try:
                config = get_pdf_config()

                options = {
                    'page-size': 'A4',
                    'margin-top': '0.5in',
                    'margin-right': '0.5in',
                    'margin-bottom': '0.5in',
                    'margin-left': '0.5in',
                    'encoding': 'UTF-8',
                    'enable-local-file-access': ''
                }

                pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)

                return send_file(
                    io.BytesIO(pdf_bytes),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=f"reporte_general_{semestre}.pdf"
                )

            except Exception as err:
                flash(f"Error generando PDF: {err}", "danger")

        return render_template("reportes/vista_previa.html", contenido=html, titulo=reporte.titulo)

    except Exception as e:
        db.session.rollback()
        flash(f"Error generando reporte: {e}", "danger")
        return redirect(url_for('reportes.general'))


# ======================================
# HISTORIAL
# ======================================

@reportes_bp.route('/historial')
@login_required
def historial():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    reportes = Reporte.query.filter_by(usuario_id=current_user.id).order_by(
        Reporte.fecha_generacion.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('reportes/historial.html', reportes=reportes)


# ======================================
# DESCARGAR DESDE HISTORIAL
# ======================================

@reportes_bp.route('/descargar/<int:reporte_id>')
@login_required
def descargar(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)

    # Seguridad
    if reporte.usuario_id != current_user.id and current_user.rol != 'administrador':
        flash("No tiene permisos para acceder a este reporte.", 'danger')
        return redirect(url_for('reportes.historial'))

    try:
        html = reporte.contenido

        config = get_pdf_config()
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
            'enable-local-file-access': ''
        }

        pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)

        filename = f"reporte_{reporte.tipo_reporte}_{reporte.id}.pdf"

        return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                         as_attachment=True, download_name=filename)

    except Exception as e:
        flash(f"Error regenerando PDF: {e}", "danger")
        return redirect(url_for("reportes.historial"))
