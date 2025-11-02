from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF
import docx2txt
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- إعدادات التطبيق ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_text_from_pdf(file_path):
    try:
        with fitz.open(file_path) as doc:
            text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def extract_text(file_path, filename):
    #  اسم الملف فيه نقطة وبيقدر ينقسم لجزئين
    if '.' in filename and len(filename.rsplit('.', 1)) == 2:
        extension = filename.rsplit('.', 1)[1].lower()
        if extension == 'pdf':
            return extract_text_from_pdf(file_path)
        elif extension in ['doc', 'docx']:
            return extract_text_from_docx(file_path)
        elif extension == 'txt':
            return extract_text_from_txt(file_path)
        else:
            # إذا اللاحقة موجودة بس غير مدعومة
            print(f"Unsupported file format: {filename}")
            return None
    else:
        # إذا الملف ما إله لاحقة أصلاً منعتبره غير مدعوم
        print(f"File has no extension: {filename}")
        return None

#  مسارات التطبيق 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/matcher', methods=['POST', 'GET']) 
def matcher():
    if request.method == 'POST':
        job_description = request.form.get('job_description', '')
        resume_files = request.files.getlist('resumes')

        if not job_description or not resume_files or resume_files[0].filename == '':
            return render_template('index.html', message="الرجاء إدخال الوصف الوظيفي ورفع ملف واحد على الأقل.")

        processed_resumes = []
        for resume_file in resume_files:
            if resume_file.filename == '':
                continue
            
            filename = secure_filename(resume_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume_file.save(filepath)
            
            text = extract_text(filepath, filename)
            
            try:
                os.remove(filepath)
            except OSError as e:
                print(f"Error deleting file {filepath}: {e}")

            if text:
                processed_resumes.append({'filename': filename, 'text': text})

        # التأكد من وجود ملفات تمت معالجتها
        if not processed_resumes:
            return render_template('index.html', message="لم يتمكن النظام من قراءة أي من الملفات المرفوعة.")
        
        resume_filenames = [r['filename'] for r in processed_resumes]
        resume_texts = [r['text'] for r in processed_resumes]

        vectorizer = TfidfVectorizer(stop_words='english') 
        vectors = vectorizer.fit_transform([job_description] + resume_texts)
        job_vector = vectors[0]
        resume_vectors = vectors[1:]

        # حساب تشابه كوزاين
        similarities = cosine_similarity(job_vector, resume_vectors)
        similarity_scores = similarities.flatten()

        results = list(zip(resume_filenames, similarity_scores.tolist()))
        
        sorted_results = sorted(results, key=lambda item: item[1], reverse=True)

        message_to_show = f"تمت معالجة {len(processed_resumes)} سيرة ذاتية بنجاح!"

        return render_template('index.html', 
                               message=message_to_show,
                               results=sorted_results)

    return render_template('index.html')


# --- تشغيل التطبيق ---
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)