from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, request
from flask_login import login_user, login_required
from . import main
from .forms import NameForm
from ..email import send_email
from ..import db
from ..models import User, Kelompok, Cleandata, Klustermodel
from .. import auth
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.io import export_png
from bokeh.embed import components
import pickle, os, sys

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
      
    if request.method == 'POST':
        test = request.form
        color = []
        kunci = []
        [color.append(test[x]) if x[:2] == "cp" else kunci.append(test[x]) for x in test]
        
        for i in range(len(color)):
            query = Kelompok.query.join(Klustermodel, Kelompok.klustermodel_id==Klustermodel.id).filter(
                Kelompok.nama==i).filter(Klustermodel.active==1).first()
            query.kuncikata = kunci[i]
            query.warna = color[i]
            db.session.commit()    

        print(color, file=sys.stderr)


    kluster = Kelompok.query.join(Klustermodel, Kelompok.klustermodel_id == 
                Klustermodel.id).add_columns(
                Kelompok.id, Kelompok.nama, Kelompok.kuncikata, Kelompok.warna,
                Klustermodel.nama).filter(Klustermodel.active==1).all()

    if kluster:
        loadbokeh = os.path.join(current_app.config['UPLOAD_BOKEH'], ''.join([kluster[0][5],'.pkl']))
        pertanyaan = []
        for i in range(len(kluster)):
            pertanyaan.append(Cleandata.query.join(
                                Kelompok, Cleandata.kelompok_id == Kelompok.id).join(
                                Klustermodel, Kelompok.klustermodel_id == Klustermodel.id).add_columns(
                                Cleandata.data_asli, Cleandata.id).filter(Kelompok.nama==i, Klustermodel.active==1).all())

        with open(loadbokeh, 'rb') as f:
            perta = pickle.load(f)

        colormap = {}

        for i in range(len(kluster)):
            colormap[i] = kluster[i][4]

        colors = [colormap[x] for x in perta['cluster']]

        p = figure(title = "Data", plot_width=650, plot_height=620)
        p.xaxis.axis_label = 'X Data'
        p.yaxis.axis_label = 'Y Data'

        source = ColumnDataSource(perta)

        p.circle(perta["xdata"],  perta["ydata"], size=17,
                 color=colors, fill_alpha=0.3)

        #labels = LabelSet(x="xdata", y="ydata", text="index", y_offset=8,
        #                  text_font_size="8pt", text_color="#555555",
        #                  source=source, text_align='center')
        #p.add_layout(labels)

        script, div = components(p)

        return render_template('admin/index.html',
                            script=script,
                            div=div,
                            legenda = kluster,
                            count = len(kluster),
                            pertanyaan=pertanyaan,
                            current_time=datetime.utcnow())

    return render_template('admin/index.html',
                            legenda = kluster)
