from flask import render_template, redirect, request, url_for, flash, session, current_app, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . import analisis
from .. import db
from ..email import send_email
from ..models import User, Cleandata, Kelompok, Vectorspace, Klustermodel, Permission
from ..decorators import permission_required
from .forms import KlusterForm
from .manalisis.stopwd import stopwords
from .manalisis.warna import warna
import sys, os, pickle, datetime
import pandas as pd


ALLOWED_EXTENSIONS = set(['csv', 'tsv'])


@analisis.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        session["nama_vektor"] = request.form['nama']
        session["stemmer"] = 'stemmer' in request.form

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename

            file.save(os.path.join(current_app.config['UPLOAD_CORPORA'], filename))
            isifile = os.path.join(current_app.config['UPLOAD_CORPORA'], filename)

            session["tmp"] = isifile

            return jsonify({ 'pesan' : 'sukses pertama' })

    form = KlusterForm()
    return render_template('admin/analisis/index.html',
                        form=form)


@analisis.route('/preproses', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def preproses():

    isifile = session["tmp"]
    stemmer = session["stemmer"]

    df = pd.read_csv(isifile, names=['ID', 'Pertanyaan'], sep=';', lineterminator='\r')
    pertanyaan = df['Pertanyaan'].values.tolist()
    id_pertanyaan = [i for i in range(51)]

    doc_stem = stopwordrem(df['Pertanyaan'].values.astype('U'))
    if stemmer:
        doc_stem = stemword(doc_stem)

    session["doc_stem"] = doc_stem

    nilai = list(zip(doc_stem, pertanyaan))
    dictionary = dict(zip(id_pertanyaan, nilai))

    pathfile = get_id('UPLOAD_DICTIONARY', session['nama_vektor'], '.pkl')
    with open(pathfile, 'wb') as f:
        pickle.dump(dictionary, f)

    return jsonify({ 'pesan' : 'sukses kedua' })


@analisis.route('/vektorisasi', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def vektorisasi():

    doc_stem = session["doc_stem"] 

    from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
    from sklearn.decomposition import PCA
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from bokeh.plotting import figure, show, output_file
    from bokeh.io import export_png
    
    tfidf_vectorizer = TfidfVectorizer(use_idf=True, ngram_range=(1,2))
    tfidf_matrix = tfidf_vectorizer.fit_transform(doc_stem)

    pipeline = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1,2))),
        ('tfidf', TfidfTransformer()),
    ])        

    X = pipeline.fit_transform(doc_stem).todense()

    pca = PCA(n_components=2).fit(X)

    data2D = pca.transform(X)
    pathfile = get_id('UPLOAD_2D', session['nama_vektor'], '.pkl')
    with open(pathfile, 'wb') as f:
        pickle.dump(data2D, f)

    p = figure(title="Visualisasi Data")
    p.background_fill_color = "#ffffff"
    p.scatter(data2D[:,0], data2D[:,1], marker="circle", size=15,
            fill_color="#2980b9", alpha=0.5)

    pathfile_png = get_id('UPLOAD_IMAGE_VEKTOR', session['nama_vektor'], '.png')
    export_png(p, filename=pathfile_png)

    pathfile = get_id('UPLOAD_VEKTOR', session['nama_vektor'], '.pkl')
    with open(pathfile, 'wb') as f:
        pickle.dump(tfidf_matrix, f)

    query = Vectorspace(nama=session['nama_vektor'])
    db.session.add(query)
    db.session.commit()

    return jsonify({ 'pesan' : 'sukses ketiga' })


@analisis.route('/klustering', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def klustering():
    
    from sklearn.metrics.pairwise import cosine_similarity
    from scipy.cluster.hierarchy import ward, dendrogram, average
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    savepkl = get_id('UPLOAD_VEKTOR', session["nama_vektor"], ".pkl")

    with open(savepkl, 'rb') as f:
        tfidf_matrix = pickle.load(f)

    isifile = session["tmp"]
    df = pd.read_csv(isifile, names=['ID', 'Pertanyaan'],
                     sep=';', lineterminator='\r')

    dist = 1 - cosine_similarity(tfidf_matrix)

    linkage_matrix = ward(dist) 

    ax = plt.subplots(figsize=(10, 10)) 
    ax = dendrogram(linkage_matrix, orientation="right", 
                    labels=df['Pertanyaan'].values.astype('U'));

    plt.tick_params(\
        axis= 'y',          
        which='both',      
        bottom='off',      
        top='off',         
        labelbottom='off')

    plt.tight_layout()

    if 'jarak' in request.form:
        plt.axvline(float(request.form['jarak']), color='black')
        t = datetime.datetime.now().time().strftime('%y%m%d%H%M%S')
        fname = ''.join([session['nama_vektor'], "_rev_", t])
        pathfile = get_id('UPLOAD_IMAGE_HIRARKI', fname, '.png')
        plt.savefig(pathfile, dpi=400)

        return jsonify({ "link" : fname })

    pathfile = get_id('UPLOAD_IMAGE_HIRARKI', session['nama_vektor'], '.png')
    plt.savefig(pathfile, dpi=400)

    return jsonify({ 'vektor': session['nama_vektor'] })


@analisis.route('/secondcluster', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def secondcluster():
    
    vektor = request.form['vektor']
    nama = request.form['nama']
    jumlah = request.form['jumlah']

    pathfile_2d = get_id('UPLOAD_2D', vektor, '.pkl')
    pathfile_tfidf = get_id('UPLOAD_VEKTOR', vektor, '.pkl')
    pathfile_dict = get_id('UPLOAD_DICTIONARY', vektor, '.pkl')

    with open(pathfile_2d, 'rb') as f:
        data2D = pickle.load(f)

    with open(pathfile_tfidf, 'rb') as f:
        tfidf_matrix = pickle.load(f)

    with open(pathfile_dict, 'rb') as f:
        dictionary = pickle.load(f)

    db.session.add(Klustermodel(nama=nama, active=0))
    db.session.commit()

    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import AgglomerativeClustering
    from sklearn import metrics
    from nltk import FreqDist
    from nltk.collocations import BigramCollocationFinder
    import numpy as np

    dist = 1 - cosine_similarity(tfidf_matrix)
    model = AgglomerativeClustering(n_clusters=int(jumlah),
                                        linkage="ward")

    model.fit(dist)

    clusters = model.labels_
    clusters_db = model.labels_.tolist()

    id_kel= [[i] for i in range(int(jumlah))]
    kelompok = [[""] for i in range(int(jumlah))]
    for i in range(len(clusters_db)):
        kelompok[clusters_db[i]][0] = ' '.join(
            [kelompok[clusters_db[i]][0], dictionary[i][0]])

    cnt = 0
    for i in range(len(kelompok)):
        kunci = []
        a = kelompok[i][0].split()
        fdist1 = FreqDist(a).most_common(1)[0][0]
        finder = BigramCollocationFinder.from_words(a, window_size = 3)

        for k,v in finder.ngram_fd.items():
            kunci.append(' '.join([k[0], k[1]]))

        mostkunci = kunci[0]

        kelompok[i].append(','.join([fdist1, mostkunci]))
        kelompok[i].append(warna[cnt])

        #kunci_ngram[i] = [warna[cnt],','.join([fdist1, mostkunci])]

        if cnt > 16:
            cnt=0
        else:
            cnt+=1

    all_kelompok = list(zip(id_kel, kelompok))
    model_id = Klustermodel.query.filter_by(
                                    nama=nama).first()
    db.session.add_all([Kelompok(nama=x[0], kuncikata=x[1][1], warna=x[1][2], 
                        klustermodel_id=model_id.id) for x in all_kelompok])
    db.session.commit()

    kel = Kelompok.query.with_entities(
                                Kelompok.nama, Kelompok.id).filter_by(
                                klustermodel_id=model_id.id).all()
    dik = dict(kel)
    kel_id = [dik[x] for x in clusters_db]
    db.session.add_all([Cleandata(
                        pertanyaan=dictionary[i][0], data_asli=dictionary[i][1], 
                        kelompok_id=kel_id[i]) for i in range(len(clusters_db))])
    db.session.commit()


    B = np.reshape(clusters, (-1, 1))
    all_data = np.append(data2D, B, 1)
    perta = pd.DataFrame(data=all_data[0:,0:], index=np.arange(
        len(all_data)), columns=['xdata', 'ydata', 'cluster'])
    gambar(perta, request.form['nama'])


    pathfile = get_id('UPLOAD_BOKEH', request.form['nama'], '.pkl')

    with open(pathfile, 'wb') as f:
        pickle.dump(perta, f)

    return jsonify({ 'formlist': 'sukses' })



@analisis.route('/getvektor', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def getvektor():
    all_vektor = Vectorspace.query.with_entities(
                    Vectorspace.id, Vectorspace.nama).all()

    return jsonify({ 'vektor': all_vektor })


def stopwordrem(words):
    import string
    exclude = set(string.punctuation)
    stop = set(stopwords)

    stopw = []
    for kalimat in words:
        punc_free = ''.join(ch for ch in kalimat if ch not in exclude)
        stop_free = " ".join([i for i in punc_free.lower().split() if i not in stop])
        
        stopw.append(stop_free)
    
    return stopw 


def stemword(docs):
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    
    stemw = []
    for kalimat in docs:
        stem = stemmer.stem(kalimat)
        stemw.append(stem)
    
    return stemw


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_id(jenis, name, ext):
    filename = ''.join([name, ext])
    savedata = os.path.join(current_app.config[jenis], filename)

    return savedata


def gambar(perta, name):
    from bokeh.plotting import figure, show, output_file
    from bokeh.models import ColumnDataSource, LabelSet
    from bokeh.io import export_png
    from bokeh.embed import components

    colormap = {0: 'red', 1: 'green', 2: 'blue',
                 3: 'orange', 4: 'yellow', 5: 'purple',
                  6: 'grey', 7: 'pink'}
    colors = [colormap[x] for x in perta['cluster']]

    p = figure(title = "Data")
    p.xaxis.axis_label = 'X Data'
    p.yaxis.axis_label = 'Y Data'

    source = ColumnDataSource(perta)

    p.circle(perta["xdata"],  perta["ydata"], size=15,
             color=colors, fill_alpha=0.2)

    #labels = LabelSet(x="xdata", y="ydata", text="index", y_offset=8,
    #                  text_font_size="8pt", text_color="#555555",
    #                  source=source, text_align='center')
    #p.add_layout(labels)

    pathfile = get_id('UPLOAD_IMAGE_CLUSTER', name, '.png')
    export_png(p, filename=pathfile)





