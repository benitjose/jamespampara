import os
import secrets
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-this-with-a-random-secret'
app.config['DATABASE'] = os.path.join(app.root_path, 'data.sqlite3')

QUESTION_SECTIONS = {
    'visual': {
        'name': 'ദൃശ്യബുദ്ധി (Visual Intelligence)',
        'questions': [
            'ചിത്രരചന എനിക്കിഷ്ടമാണ്.',
            'എനിക്ക് വഴികൾ എളുപ്പത്തിൽ ഓർത്തിരിക്കാൻ കഴിയും',
            'ചിത്രങ്ങൾ കാണിച്ച് പഠിപ്പിക്കുമ്പോൾ എനിക്ക് പെട്ടെന്ന് മനസ്സിലാകും',
            'ഞാൻ കണ്ട സ്ഥലങ്ങളുടെ രൂപരേഖ എൻ്റെ മനസ്സിൽ നിലനിൽക്കുന്നു',
            'രൂപങ്ങൾ തമ്മിലുള്ള സാമ്യവും വ്യത്യാസവും എനിക്ക് വേഗത്തിൽ തിരിച്ചറിയാൻ കഴിയും',
            'ഒരു മുറിയിലെ ഫർണിച്ചറുകൾ എങ്ങനെ ക്രമീകരിച്ചാൽ കൂടുതൽ ഭംഗിയാകും എന്ന് എനിക്ക് നിർദേശിക്കാൻ കഴിയും.',
            'പഠിക്കുമ്പോൾ അതിൻ്റെ ചിത്രങ്ങൾ മനസ്സിൽ രൂപപ്പെടാറുണ്ട്.',
            'പസിലുകളും രൂപപരിചയ കളികളും എനിക്ക് ഇഷ്ട‌മാണ്.',
            'രൂപങ്ങളും ആകൃതികളും തമ്മിലുള്ള വ്യത്യാസം എനിക്ക് മനസ്സിലാക്കാൻ കഴിയും.',
            'അലങ്കാര ക്രമീകരണങ്ങളിൽ എനിക്ക് താൽപര്യമുണ്ട്.'
        ]
    },
    'verbal': {
        'name': 'ഭാഷാ ബുദ്ധി(Verbal / Linguistic Intelligence)',
        'questions': [
            'പ്രസംഗങ്ങൾ ഞാൻ ശ്രദ്ധിച്ച് കേൾക്കാറുണ്ട്.',
            'ഭാഷാപരമായ വിഷയങ്ങൾ എനിക്ക് ഇഷ്‌ടമാണ്.',
            'ഞാൻ വായിച്ച കാര്യങ്ങൾ മറ്റുള്ളവരോട് പങ്കു വയ്ക്കാറുണ്ട്.',
            'ഒരു കാര്യം പറയുന്നതിന് മുമ്പ് ഞാൻ അത് മനസ്സിൽ പറഞ്ഞുനോക്കാറുണ്ട്.',
            'കഥകൾ കേൾക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'കഥ പറയാൻ എനിക്കിഷ്‌ടമാണ്.',
            'കവിതകളും ലേഖനങ്ങളും എഴുതാൻ എനിക്ക് താൽപര്യമുണ്ട്.', 
            'പുതിയ വാക്കുകളുടെ അർത്ഥം അറിയാൻ ഞാൻ ശ്രമിക്കാറുണ്ട്.',
            'ചർച്ചകളിൽ സംസാരിക്കാൻ എനിക്ക് ഇഷ്‌ടമാണ്.',
            'പുസ്‌തകവായന എനിക്ക് ഇഷ്ടമാണ്.'
        ]
    },
    'logical': {
        'name': 'താർക്കിക-ഗണിത ബുദ്ധി (Logical Intelligence)',
        'questions': [
            'കണക്കും സയൻസും എനിക്ക് എളുപ്പമാണ്.',
            'ശാസ്ത്രത്തിലെ പുതിയ കണ്ടെത്തലുകൾ ഞാൻ ശ്രദ്ധിക്കാറുണ്ട്.',
            'ഉപകരണങ്ങളുടെ പ്രവർത്തനം മനസ്സിലാക്കാൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'പ്രശ്നങ്ങൾക്ക് കാരണം കണ്ടെത്താൻ ഞാൻ ശ്രമിക്കാറുണ്ട്.',
            'പരീക്ഷണങ്ങൾ നടത്താൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'കമ്പ്യൂട്ടർ പ്രവർത്തനങ്ങൾ എനിക്ക് ഇഷ്ടമാണ്.',
            'വരവു -ചെലവ് കണക്കുകൾ മനസ്സിലാക്കാൻ എനിക്ക് കഴിയും.',
            'ഒരു കാര്യത്തെ ഘട്ടംഘട്ടമായി ചിന്തിക്കാൻ എനിക്ക് കഴിയും.',
            'ക്വിസ്, ബ്രെയിൻ ഗെയിംസ് എന്നിവ എനിക്ക് ഇഷ്ടമാണ്.',
            'കൃത്യമായ ഉത്തരങ്ങൾ കണ്ടെത്താൻ ഞാൻ ശ്രമിക്കാറുണ്ട്.',
        ]
    },
    'kinesthetic': {
        'name': 'ശാരീരിക-ചലന ബുദ്ധി (Kinesthetic Intelligence)',
        'questions': [
            'ഞാൻ സ്ഥിരമായി സ്പോർട്‌സ് പരിശീലിക്കാറുണ്ട്.',
            'നൃത്തം, നാടകം തുടങ്ങിയവയിൽ പങ്കെടക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'കൈകൊണ്ട് നിർമ്മിക്കുന്ന പ്രവർത്തനങ്ങൾ എനിക്ക് ഇഷ്ടമാണ്.',
            'സംസാരിക്കുമ്പോൾ കൈചലനങ്ങൾ ഉപയോഗിക്കാറുണ്ട്.',
            'ശാരീരിക പ്രവർത്തനങ്ങളിൽ പങ്കെടുക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'പൊട്ടിയ സാധനങ്ങൾ ശരിയാക്കാൻ ഞാൻ ശ്രമിക്കാറുണ്ട്.',
            'നടക്കുമ്പോൾ എനിക്ക് പുതിയ ആശയങ്ങൾ വരാറുണ്ട്.',
            'പ്രായോഗികമായി പഠിക്കുമ്പോൾ എനിക്ക് കൂടുതൽ മനസ്സിലാകും.',
            'ദീർഘസമയം ഒരേ സ്ഥലത്ത് ഇരിക്കാൻ എനിക്ക് ബുദ്ധിമുട്ടുണ്ട്.',
            'ശരീരചലനങ്ങളിലൂടെ കാര്യങ്ങൾ പ്രകടിപ്പിക്കാൻ എനിക്ക് കഴിയും.'
        ]
    },
    'rhythmic': {
        'name': 'സംഗീതബുദ്ധി (Rhythmic / Musical Intelligence)',
        'questions': [
            'സംഗീതം കേൾക്കാൻ എനിക്ക് വളരെ ഇഷ്ടമാണ്.',
            'താളം എളുപ്പത്തിൽ തിരിച്ചറിയാൻ എനിക്ക് കഴിയും.',
            'ജോലി ചെയ്യുമ്പോൾ ഞാൻ പാട്ട് മൂളാറുണ്ട്.',
            'സംഗീതപരിപാടികൾ ഞാൻ ശ്രദ്ധിക്കാറുണ്ട്.',
            'പാട്ടുകളുടെ വരികൾ എനിക്ക് എളുപ്പത്തിൽ ഓർമ്മയിൽ നിൽക്കും.',
            'പാട്ട്/സംഗീത മത്സരങ്ങളിൽ പങ്കെടുക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'വിഷമസമയങ്ങളിൽ പാട്ട് കേൾക്കുന്നത് എനിക്ക് ആശ്വാസമാണ്.',
            'പുതിയ പാട്ടുകൾ പഠിക്കാൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'സംഗീതോപകരണങ്ങൾ ഉപയോഗിക്കാൻ എനിക്ക് ഇഷ്‌ടമാണ്.',
            'ഒരു ശബ്ദത്തിലെ താളവ്യത്യാസം എനിക്ക് തിരിച്ചറിയാൻ കഴിയും.'
        ]
    },
    'interpersonal': {
        'name': 'സാമൂഹിക ബുദ്ധി(Interpersonal intelligence)',
        'questions': [
            'മറ്റുള്ളവരോടൊപ്പം പ്രവർത്തിക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'മറ്റുള്ളവരുടെ വികാരങ്ങൾ എനിക്ക് മനസ്സിലാക്കാൻ കഴിയും.',
            'ആളുകൾ എൻ്റെ അഭിപ്രായം ചോദിക്കാറുണ്ട്.',
            'പൊതു പ്രവർത്തനങ്ങളിൽ പങ്കെടുക്കാൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'മറ്റുള്ളവരെ സഹായിക്കാൻ ഞാൻ തയ്യാറാകാറുണ്ട്.',
            'പുതിയ ആളുകളുമായി എളുപ്പത്തിൽ ഇടപഴകാൻ എനിക്ക് കഴിയും.',
            'മറ്റുള്ളവരെ പ്രോത്സാഹിപ്പിക്കാൻ എനിക്ക് കഴിയും.',
            'കൂട്ടായ പ്രവർത്തനങ്ങളിൽ നേതൃത്വം ഏറ്റെടുക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'വഴക്കുകൾ പരിഹരിക്കാൻ ഞാൻ ശ്രമിക്കാറുണ്ട്.',
            'സുഹൃത്തുക്കളുമായി സമയം ചെലവഴിക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.'
        ]
    },
    'intrapersonal': {
        'name': 'ആത്മബോധ ബുദ്ധി (Intrapersonal Intelligence)',
        'questions': [
            'തനിച്ചിരുന്ന് സമയം ചെലവഴിക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'എന്റെ കഴിവുകൾ എനിക്ക് വ്യക്തമായി അറിയാം.',
            'എന്റെ ഭാവിയെക്കുറിച്ച് എനിക്ക് വ്യക്തമായ ലക്ഷ്യമുണ്ട്.',
            'എന്റെ അഭിപ്രായത്തിൽ ഞാൻ ഉറച്ചു നിൽക്കാറുണ്ട്.',
            'എനിക്ക് ഇഷ്ടമുള്ള ഹോബികൾ ഉണ്ട്.',
            'എന്റെ ജീവിതലക്ഷ്യം നേടാൻ ഞാൻ പരിശ്രമിക്കാറുണ്ട്.',
            'എന്റെ ശക്തിയും ദൗർബല്യവും എനിക്ക് അറിയാം.',
            'എന്റെ വികാരങ്ങൾ നിയന്ത്രിക്കാൻ എനിക്ക് കഴിയും.',
            'തെറ്റുകൾ സംഭവിച്ചാൽ ഞാൻ സ്വയം വിലയിരുത്താറുണ്ട്.',
            'ഞാൻ സ്വയം തീരുമാനങ്ങൾ എടുക്കാൻ ശ്രമിക്കാറുണ്ട്.'
        ]
    },
    'naturalistic': {
        'name': 'പ്രകൃതി ബുദ്ധി (Naturalistic Intelligence)',
        'questions': [
            'പുറംപരിസരങ്ങളിൽ സമയം ചെലവഴിക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'ചെടികൾ വളർത്താൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'വളർത്തുമൃഗങ്ങളെ പരിപാലിക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'പ്രകൃതിയിലെ പ്രത്യേകതകൾ ഞാൻ ശ്രദ്ധിക്കാറുണ്ട്.',
            'കാലാവസ്ഥയിലെ മാറ്റങ്ങൾ ഞാൻ ശ്രദ്ധിക്കാറുണ്ട്.',
            'പ്രകൃതി സംരക്ഷണ പ്രവർത്തനങ്ങളിൽ പങ്കെടുക്കാൻ എനിക്ക് ഇഷ്ട‌മാണ്.',
            'വന്യജീവികളെക്കുറിച്ച് അറിയാൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'പ്രകൃതി ചിത്രങ്ങൾ കാണാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'മണ്ണ്, മഴ, സസ്യങ്ങൾ എന്നിവയെക്കുറിച്ച് പഠിക്കാൻ എനിക്ക് ഇഷ്ട്‌ടമാണ്.',
            'യാത്രകളിൽ പ്രകൃതി ഭംഗി ഞാൻ ആസ്വദിക്കാറുണ്ട്.'
        ]
    },
    'Digital': {
        'name': 'ഡിജിറ്റൽ ഇന്റലിജൻസ് (Digital Intelligence)',
        'questions': [
            'പഠനത്തിനായി ഓൺലൈൻ പ്ലാറ്റ്‌ഫോമുകൾ ഞാൻ ഉപയോഗിക്കാറുണ്ട്.',
            'ഡിജിറ്റൽ പഠനസാമഗ്രികൾ തയ്യാറാക്കാൻ എനിക്ക് കഴിയും.',
            'ഓൺലൈൻ സുരക്ഷയുടെ പ്രാധാന്യം എനിക്ക് അറിയാം.',
            'വ്യാജ ലിങ്കുകളും ഓൺലൈൻ തട്ടിപ്പുകളും തിരിച്ചറിയാൻ എനിക്ക് കഴിയും.',
            'ഓൺലൈൻ  ആശയ വിനിമയത്തിൽ ഞാൻ ഉത്തരവാദിത്തത്തോടേ പെരുമാറാറുണ്ട്. ',
            'ഡിജിറ്റൽ ഉപകരണങ്ങളിലൂടേ ആശയങ്ങൾ അവതരിപ്പിക്കാൻ എനിക്ക് കഴിയും.',
            'സോഷ്യൽ മീഡിയ വിവേകത്തോടെ ഉപയോഗിക്കണം എന്ന് ഞാൻ വിശ്വസിക്കുന്നു.',
            'പുതിയ ആപ്പുകൾ ഉപയോഗിക്കാൻ ഞാൻ വേഗത്തിൽ പഠിക്കും.',
            'ഇന്റർനെറ്റിൽ നിന്നും വിവരങ്ങൾ തിരയാൻ എനിക്ക് കഴിയും.',
            'സാങ്കേതികവിദ്യ ഉപയോഗിച്ച് പ്രശ്‌നപരിഹാരം ചെയ്യാൻ എനിക്ക് ഇഷ്ടമാണ്.'
        ]
    },
    'Enterprising': {
        'name': 'നേതൃ / സംരംഭക ബുദ്ധി (Enterprising Intelligence)',
        'questions': [
            'ഗ്രൂപ്പ് പ്രവർത്തനങ്ങളിൽ നേത്യത്വം എടുക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'മറ്റുള്ളവരെ ബോധ്യപ്പെടുത്താൻ എനിക്ക് കഴിയും.',
            'പരിപാടികൾ സംഘടിപ്പിക്കാൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'പ്രശ്നങ്ങൾക്ക് പുതിയ പരിഹാരങ്ങൾ കണ്ടെത്താൻ ഞാൻ ശ്രമിക്കാറുണ്ട്.',
            'ലാഭനഷ്ടങ്ങളെക്കുറിച്ച് ചിന്തിക്കാൻ എനിക്ക് താൽപര്യമുണ്ട്.',
            'വിൽപ്പന പ്രവർത്തനങ്ങളിൽ പങ്കെടുക്കാൻ എനിക്ക് ഇഷ്ടമാണ്.',
            'പുതിയ ആശയങ്ങൾ അവതരിപ്പിക്കാൻ എനിക്ക് ധൈര്യമുണ്ട്.',
            'റിസ്ക് എടുക്കാൻ ഞാൻ തയ്യാറാകാറുണ്ട്.',
            'ചെറിയ ബിസിനസ് ആശയങ്ങളേക്കുറിച്ച് ഞാൻ ചിന്തിക്കാറുണ്ട്.',
            'ആളുകളെ നയിക്കാൻ എനിക്ക് കഴിയും.'
        ]
    }
}

ADMIN_EMAIL = 'james@pampara'
ADMIN_PASSWORD = '123@pampara'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)


def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            dob TEXT
        );

        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            section TEXT NOT NULL,
            question_index INTEGER NOT NULL,
            answer INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, section, question_index),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    ''')
    # Add dob column if not exists
    try:
        db.execute('ALTER TABLE users ADD COLUMN dob TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Add class column if not exists
    try:
        db.execute('ALTER TABLE users ADD COLUMN class TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Add school column if not exists
    try:
        db.execute('ALTER TABLE users ADD COLUMN school TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Add PIN code column if not exists
    try:
        db.execute('ALTER TABLE users ADD COLUMN pin_code TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    existing_admin = db.execute('SELECT id FROM users WHERE email = ?', (ADMIN_EMAIL,)).fetchone()
    if existing_admin is None:
        db.execute(
            'INSERT INTO users (name, email, password_hash, is_admin, dob) VALUES (?, ?, ?, ?, ?)',
            ('Admin', ADMIN_EMAIL, generate_password_hash(ADMIN_PASSWORD), 1, '')
        )
        db.commit()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_section_stats(answer_map, section_id):
    questions = QUESTION_SECTIONS[section_id]['questions']
    answers = answer_map.get(section_id, {})
    answered = len(answers)
    average = round(sum(answers.values()) / answered, 1) if answered else 0
    return {
        'answered': answered,
        'total': len(questions),
        'average': average
    }

def get_section_sum(answer_map, section_id):
    questions = QUESTION_SECTIONS[section_id]['questions']
    answers = answer_map.get(section_id, {})
    answered = len(answers)
    total = sum(answers.values()) if answers else 0
    return {
        'answered': answered,
        'total': len(questions),
        'sum': total
    }


def login_required(view):
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


def admin_required(view):
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = query_db('SELECT * FROM users WHERE id = ?', (session['user_id'],), one=True)
        if user is None or not user['is_admin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


@app.before_request
def before_request():
    init_db()


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.context_processor
def inject_sections():
    return {'question_sections': QUESTION_SECTIONS}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        dob = request.form.get('dob', '').strip()
        class_field = request.form.get('class', '').strip()
        school = request.form.get('school', '').strip()
        consent = request.form.get('consent')
        if not name or not email or not dob:
            flash('Name, email, and date of birth are required.', 'danger')
            return render_template('index.html')
        if not consent:
            flash('You must consent to the privacy notice to proceed.', 'danger')
            return render_template('index.html')
        user = query_db('SELECT id FROM users WHERE email = ?', (email,), one=True)
        if user:
            flash('This email has already been used. Please contact admin if you need to update.', 'danger')
            return render_template('index.html')
        db = get_db()
        db.execute(
            'INSERT INTO users (name, email, password_hash, dob, class, school) VALUES (?, ?, ?, ?, ?, ?)',
            (name, email, '', dob, class_field, school)
        )
        db.commit()
        flash('Registration successful. Please enter the one-time PIN provided by the admin.', 'success')
        return redirect(url_for('verify_pin', email=email))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
        if user:
            if user['is_admin']:
                if user['password_hash'] and check_password_hash(user['password_hash'], password):
                    session.clear()
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['is_admin'] = True
                    return redirect(url_for('admin'))
            else:
                if user['pin_code'] and password == user['pin_code']:
                    db = get_db()
                    db.execute('UPDATE users SET pin_code = NULL WHERE id = ?', (user['id'],))
                    db.commit()
                    session.clear()
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['is_admin'] = False
                    return redirect(url_for('dashboard'))
        flash('Invalid email or PIN. Ask admin for a one-time PIN to login.', 'danger')
    return render_template('login.html')


@app.route('/admin_login', methods=['POST'])
def admin_login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    if not email or not password:
        flash('Admin email and password are required.', 'danger')
        return render_template('index.html', show_admin_login=True)
    if email != ADMIN_EMAIL:
        flash('Unauthorized admin login.', 'danger')
        return render_template('index.html', show_admin_login=True)

    user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
    if user and user['is_admin'] and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['is_admin'] = True
        return redirect(url_for('admin'))

    flash('Unauthorized admin login.', 'danger')
    return render_template('index.html', show_admin_login=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        consent = request.form.get('consent')
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        elif not consent:
            flash('You must agree to the data collection and privacy terms to register.', 'danger')
        elif query_db('SELECT id FROM users WHERE email = ?', (email,), one=True):
            flash('Email already registered.', 'danger')
        else:
            db = get_db()
            db.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful. Please enter the one-time PIN provided by admin.', 'success')
            return redirect(url_for('verify_pin', email=email))
    return render_template('register.html')


@app.route('/verify_pin', methods=['GET', 'POST'])
def verify_pin():
    email = request.args.get('email', '') if request.method == 'GET' else request.form.get('email', '').strip().lower()
    pin_code = request.form.get('pin_code', '').strip()
    if request.method == 'POST':
        if not email or not pin_code:
            flash('Email and one-time PIN are both required.', 'danger')
            return render_template('verify_pin.html', email=email)
        user = query_db('SELECT * FROM users WHERE email = ? AND is_admin = 0', (email,), one=True)
        if user and user['pin_code'] and pin_code == user['pin_code']:
            db = get_db()
            db.execute('UPDATE users SET pin_code = NULL WHERE id = ?', (user['id'],))
            db.commit()
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = False
            flash('PIN verified. You are now logged in and can start the assessment.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or one-time PIN. Please verify the PIN with admin.', 'danger')
    return render_template('verify_pin.html', email=email)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    section_status = {}
    section_progress = {}
    total_answered = 0
    total_questions = sum(len(section['questions']) for section in QUESTION_SECTIONS.values())
    completed_sections = 0

    for key, section in QUESTION_SECTIONS.items():
        total = len(section['questions'])
        answered = query_db(
            'SELECT COUNT(*) AS cnt FROM answers WHERE user_id = ? AND section = ?',
            (user_id, key), one=True
        )['cnt']
        section_status[key] = answered == total
        if answered == total:
            completed_sections += 1
        section_progress[key] = {
            'answered': answered,
            'total': total,
            'percent': int(round(answered / total * 100))
        }
        total_answered += answered

    overall_percent = int(round(total_answered / total_questions * 100)) if total_questions else 0
    return render_template(
        'dashboard.html',
        section_status=section_status,
        section_progress=section_progress,
        overall_percent=overall_percent,
        completed_sections=completed_sections,
        total_sections=len(QUESTION_SECTIONS)
    )


@app.route('/sessions')
@login_required
def sessions():
    user_id = session['user_id']
    section_status = {}
    section_progress = {}
    total_answered = 0
    total_questions = sum(len(section['questions']) for section in QUESTION_SECTIONS.values())
    completed_sections = 0

    for key, section in QUESTION_SECTIONS.items():
        total = len(section['questions'])
        answered = query_db(
            'SELECT COUNT(*) AS cnt FROM answers WHERE user_id = ? AND section = ?',
            (user_id, key), one=True
        )['cnt']
        section_status[key] = answered == total
        if answered == total:
            completed_sections += 1
        section_progress[key] = {
            'answered': answered,
            'total': total,
            'percent': int(round(answered / total * 100))
        }
        total_answered += answered

    overall_percent = int(round(total_answered / total_questions * 100)) if total_questions else 0
    return render_template(
        'sessions.html',
        section_status=section_status,
        section_progress=section_progress,
        overall_percent=overall_percent,
        completed_sections=completed_sections,
        total_sections=len(QUESTION_SECTIONS)
    )


@app.route('/section/<section_id>', methods=['GET', 'POST'])
@login_required
def section(section_id):
    if section_id not in QUESTION_SECTIONS:
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    # Check if user has completed all sections
    total_sections = len(QUESTION_SECTIONS)
    completed_sections = 0
    for key in QUESTION_SECTIONS:
        answered = query_db(
            'SELECT COUNT(*) AS cnt FROM answers WHERE user_id = ? AND section = ?',
            (user_id, key), one=True
        )['cnt']
        if answered == len(QUESTION_SECTIONS[key]['questions']):
            completed_sections += 1
    if completed_sections == total_sections:
        flash('You have completed the assessment. You can view your answers in your profile.', 'info')
        return redirect(url_for('dashboard'))
    section_data = QUESTION_SECTIONS[section_id]
    existing_answers = {row['question_index']: row['answer'] for row in query_db(
        'SELECT question_index, answer FROM answers WHERE user_id = ? AND section = ?',
        (user_id, section_id)
    )}
    if request.method == 'POST':
        answers = {}
        for idx in range(len(section_data['questions'])):
            value = request.form.get(f'question_{idx}')
            if value is None or value not in ('1', '2', '3', '4', '5'):
                flash('തുടരുന്നതിന് മുമ്പ് ദയവായി എല്ലാ ചോദ്യങ്ങൾക്കും ഉത്തരം നൽകുക.', 'danger')
                return render_template('section.html', section_id=section_id, section=section_data, answers=existing_answers)
            answers[idx] = int(value)
        db = get_db()
        for idx, value in answers.items():
            db.execute('''
                INSERT INTO answers (user_id, section, question_index, answer)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, section, question_index) DO UPDATE SET answer = excluded.answer
            ''', (user_id, section_id, idx, value))
        db.commit()
        flash(f'{section_data["name"]} answers saved successfully.', 'success')
        return redirect(url_for('sessions'))
    return render_template('section.html', section_id=section_id, section=section_data, answers=existing_answers)


@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    rows = query_db('SELECT section, question_index, answer FROM answers WHERE user_id = ? ORDER BY section, question_index', (user_id,))
    grouped = {}
    for row in rows:
        grouped.setdefault(row['section'], {})[row['question_index']] = row['answer']

    section_stats = {
        section_id: get_section_stats(grouped, section_id)
        for section_id in QUESTION_SECTIONS
    }
    total_answered = sum(stats['answered'] for stats in section_stats.values())
    total_questions = sum(stats['total'] for stats in section_stats.values())
    overall_average = round(
        sum(sum(grouped.get(section_id, {}).values()) for section_id in grouped) / total_answered,
        1
    ) if total_answered else 0

    return render_template(
        'profile.html',
        answers=grouped,
        section_stats=section_stats,
        total_answered=total_answered,
        total_questions=total_questions,
        overall_average=overall_average
    )


@app.route('/submit')
@login_required
def submit_assessment():
    user_id = session['user_id']
    completed_sections = 0
    for key in QUESTION_SECTIONS:
        answered = query_db(
            'SELECT COUNT(*) AS cnt FROM answers WHERE user_id = ? AND section = ?',
            (user_id, key), one=True
        )['cnt']
        if answered == len(QUESTION_SECTIONS[key]['questions']):
            completed_sections += 1

    if completed_sections != len(QUESTION_SECTIONS):
        flash('Please complete all sections before submitting.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('submit.html')


@app.route('/admin')
@admin_required
def admin():
    all_users = query_db('SELECT id, name, email, is_admin FROM users ORDER BY name')
    users = []
    for user in all_users:
        if user['is_admin']:
            continue  # Skip admin users
        total_answers = query_db(
            'SELECT COUNT(*) AS cnt FROM answers WHERE user_id = ?',
            (user['id'],), one=True
        )['cnt']
        total_score = query_db(
            'SELECT SUM(answer) AS sum FROM answers WHERE user_id = ?',
            (user['id'],), one=True
        )['sum']
        completed = 0
        for key, section in QUESTION_SECTIONS.items():
            section_total = len(section['questions'])
            section_answers = query_db(
                'SELECT COUNT(*) AS cnt FROM answers WHERE user_id = ? AND section = ?',
                (user['id'], key), one=True
            )['cnt']
            if section_answers == section_total:
                completed += 1
        users.append({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'is_admin': bool(user['is_admin']),
            'answers_count': total_answers,
            'completed_sections': completed,
            'total_score': int(total_score) if total_score is not None else 0
        })

    return render_template('admin.html', users=users)


@app.route('/admin/user/<int:user_id>/generate_pin', methods=['POST'])
@admin_required
def admin_generate_pin(user_id):
    user = query_db('SELECT id, name FROM users WHERE id = ?', (user_id,), one=True)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('admin'))

    new_pin = ''.join(secrets.choice('0123456789') for _ in range(6))
    db = get_db()
    db.execute('UPDATE users SET pin_code = ? WHERE id = ?', (new_pin, user_id))
    db.commit()
    flash(f'Generated a new login PIN for {user["name"]}: {new_pin}', 'success')
    return redirect(url_for('admin_user', user_id=user_id))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin'))
    user = query_db('SELECT id, name FROM users WHERE id = ?', (user_id,), one=True)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('admin'))
    db = get_db()
    db.execute('DELETE FROM answers WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    flash(f'User {user["name"]} and all their responses have been deleted.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_user(user_id):
    user = query_db('SELECT id, name, email, dob, class, school, pin_code FROM users WHERE id = ?', (user_id,), one=True)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('admin'))
    answers = query_db(
        'SELECT section, question_index, answer FROM answers WHERE user_id = ? ORDER BY section, question_index',
        (user_id,)
    )
    grouped = {}
    for row in answers:
        grouped.setdefault(row['section'], {})[row['question_index']] = row['answer']

    section_summary = {
        section_id: get_section_sum(grouped, section_id)
        for section_id in QUESTION_SECTIONS
    }
    all_answers = [row['answer'] for row in answers]
    overall_total = sum(all_answers) if all_answers else 0
    return render_template(
        'admin_user.html',
        user=user,
        grouped_answers=grouped,
        sections=QUESTION_SECTIONS,
        section_summary=section_summary,
        overall_total=overall_total
    )


if __name__ == '__main__':
    app.run(debug=True)
