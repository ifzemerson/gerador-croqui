from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for, jsonify
from reportlab.pdfgen import canvas
from pdfrw import PdfReader, PdfWriter, PageMerge
from pathlib import Path
import re, random, os, json
import asyncio
from telethon import TelegramClient

# --- BIBLIOTECAS DE MAPA ---
from geopy.geocoders import Nominatim, ArcGIS, GoogleV3
from geopy.exc import GeocoderTimedOut

app = Flask(__name__)
app.secret_key = "1307"

# --- CONFIGURAÇÃO DA CHAVE DO GOOGLE MAPS ---
GOOGLE_API_KEY = "AIzaSyCZXAgi1EQntbx7U3SyZI3I4xWj25E2sq0"

TEMPLATE_PDF = "CROQUI.pdf"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================
# CONFIGURAÇÕES DO TELEGRAM
# ==========================================
TELEGRAM_API_ID = 33091552
TELEGRAM_API_HASH = 'd09dcafbf4b9ba5427d80e5b4cad5837'
TELEGRAM_GROUP_IDS = [-4209680542, -4112543320]
TELEGRAM_SESSION = 'sessao_usuario'

# ==========================================
# BANCO DE DADOS DE TÉCNICOS
# ==========================================
DB_TECNICOS = {
    # --- AREA 15 ---
    "agnaldo venancio brisola": {"re": "0102060458", "area": "15"},
    "alessandro ferreira de morais": {"re": "0102047065", "area": "15"},
    "cleiton irani rodrigues benfica": {"re": "0102059450", "area": "15"},
    "emerson pereira da silva": {"re": "0102059848", "area": "15"},
    "erickson fernando leme": {"re": "0102053031", "area": "15"},
    "joaquim otavio machado vaz": {"re": "0102063826", "area": "15"},
    "julio cesar mendes de moraes": {"re": "0102050030", "area": "15"},
    "leandro dias da costa junior": {"re": "0102055139", "area": "15"},
    "leonardo félix cruz junior": {"re": "0102063528", "area": "15"},
    "marcos paulo dos santos": {"re": "0124064676", "area": "15"},
    "murilo de oliveira fructuosoda graça": {"re": "0102063941", "area": "15"},
    "pablo daniel amaro antonio": {"re": "0102059303", "area": "15"},
    "roger ribeiro gomes": {"re": "0102054899", "area": "15"},
    "ruan augusto dos santos caetano": {"re": "0124064626", "area": "15"},
    "talissa aparecida barbosa de andrade": {"re": "0102044461", "area": "15"},
    "welington josé domimgues batista": {"re": "0102047056", "area": "15"},
    "edenilson santos": {"re": "0124065541", "area": "15"},
    "samuel vinícius de castro gomes": {"re": "0124065786", "area": "15"},
    "lucas gabriel de almeida ramos": {"re": "0102063402", "area": "15"},

    # --- AREA 11 ---
    "aguilson lucas nunes moreira": {"re": "0102062737", "area": "11"},
    "alan almeida jesus": {"re": "0102062248", "area": "11"},
    "alan bruno de oliveira": {"re": "0118065433", "area": "11"},
    "alex feitosa monteiro": {"re": "0102064113", "area": "11"},
    "caio rodrigo de souza goncalves": {"re": "0118064757", "area": "11"},
    "diogo primo silva": {"re": "0102056374", "area": "11"},
    "edmilson dos santos pereira": {"re": "0102060449", "area": "11"},
    "edson rosa vieira": {"re": "0118064670", "area": "11"},
    "elias fonseca maciel de melo": {"re": "0118064645", "area": "11"},
    "felipe fontoura silva": {"re": "102062731", "area": "11"},
    "felipe nunes barbosa da silva": {"re": "0102063906", "area": "11"},
    "fernando aparecido camargo ferreira": {"re": "0102060636", "area": "11"},
    "henrique de lima andrade": {"re": "102063911", "area": "11"},
    "joao gabriel furtado feitosa": {"re": "0118065540", "area": "11"},
    "jonathan dos santos fernandes rodrigues": {"re": "0102060445", "area": "11"},
    "jose gabriel da silva neto": {"re": "0102060418", "area": "11"},
    "julio cesar silva de oliveira": {"re": "102060638", "area": "11"},
    "jurandi wesley batista da silva": {"re": "0118064679", "area": "11"},
    "kelvin gomes da silva": {"re": "0102062255", "area": "11"},
    "lucas amorim gomes": {"re": "0118064689", "area": "11"},
    "marcio barbosa lima": {"re": "0102062727", "area": "11"},
    "marco de lucca tavares guimaraes": {"re": "0102062770", "area": "11"},
    "mauricio oliveira fernandes": {"re": "0118064616", "area": "11"},
    "ruan vinicius fonseca fonteles": {"re": "0102064131", "area": "11"},
    "wendel ribeiro bueno": {"re": "0102064177", "area": "11"},

    # --- AREA 12 ---
    "clovis mateus de aguiar": {"re": "0102059436", "area": "12"},
    "ederval jose fernandes": {"re": "0102055514", "area": "12"},
    "francisco guilherme dos santos": {"re": "0102052569", "area": "12"},
    "gabriel de souza sepulveda": {"re": "0102056361", "area": "12"},
    "luciano de andrade brison": {"re": "0102052551", "area": "12"},
    "rondineli anderson ribeiro": {"re": "0118065535", "area": "12"},
    "adair victor moreira ribeiro": {"re": "0118064698", "area": "12"},
    "andre luiz de araujo": {"re": "0102047050", "area": "12"},
    "charles campos de oliveira": {"re": "0102060469", "area": "12"},
    "daniel de oliveira leandro": {"re": "0102047088", "area": "12"},
    "diego wenceslau": {"re": "0102063949", "area": "12"},
    "felipe domingos juliani": {"re": "0102047043", "area": "12"},
    "gilson bandeira campos junior": {"re": "0102060965", "area": "12"},
    "leonardo nunes ribeiro da silva": {"re": "0102060345", "area": "12"},
    "matheus das neves campos": {"re": "0102059444", "area": "12"},
    "rodolfo de oliveira pereira": {"re": "0102060964", "area": "12"},
    "rodrigo tavares": {"re": "0102056375", "area": "12"},
    "acir francisco clemente": {"re": "0102053070", "area": "12"},
    "alexandre de souza praxedes": {"re": "0102053587", "area": "12"},
    "bruno freita dos santos": {"re": "0102064488", "area": "12"},
    "claudemir francisco da silva": {"re": "0102061210", "area": "12"},
    "heliomar bessa de oliveira": {"re": "0102052589", "area": "12"},
    "jackson tadeu carlos": {"re": "0102046989", "area": "12"},
    "jefferson christian castilho": {"re": "0102064523", "area": "12"},
    "joao marcos augusto flausino": {"re": "0102064491", "area": "12"},
    "kelvin aparecido da silva": {"re": "0102064109", "area": "12"},
    "lemuel de paula rodrigues": {"re": "0102064507", "area": "12"},
    "max william de castro da silva": {"re": "0102064490", "area": "12"},
    "renato dos santos": {"re": "0102047067", "area": "12"},
    "samuel antonio de siqueira": {"re": "0102047061", "area": "12"},
    "silas de araujo rocha": {"re": "0102047063", "area": "12"}
}

DB_ALIASES = {
    "edenilson": "edenilson santos", "edenilson de souza": "edenilson santos",
    "cleber": "cleiton irani rodrigues benfica"
}

DB_VEICULOS = {
    "leonardo félix cruz junior": "RVW5G87",
    "leandro dias da costa junior": "RVI3G26",
    "murilo de oliveira fructuosoda graça": "RTR3F69",
    "agnaldo venancio brisola": "RTR3F69",
    "emerson pereira da silva": "RVQ0G58",
    "pablo daniel amaro antonio": "RTI7C83",
    "alessandro ferreira de morais": "RVJ6D74",
    "roger ribeiro gomes": "RVI3G26",
    "julio cesar mendes de moraes": "RVJ6D77",
    "cleiton irani rodrigues benfica": "RUX6C72"
}

# --- CONFIGURAÇÕES DE PDF ---
COORDS = {
    'codigo_obra': (0.18, 0.039),
    'ta': (0.20, 0.182),
    'causa': (0.17, 0.152),
    'endereco': (0.17, 0.125),
    'localidade': (0.11, 0.096),
    'es': (0.28, 0.096),
    'at': (0.34, 0.096),
    'tronco': (0.10, 0.067),
    'veiculo': (0.47, 0.040),
    'supervisor': (0.63, 0.040),
    'data': (0.83, 0.049),
    'materials_block': (0.045, 0.33),
    'croqui_rect': (0.02, 0.65, 0.95, 0.90)
}

EXEC_CONFIG = {'name_x': 0.47, 're_x': 0.65, 'start_y': 0.212, 'step_y': 0.028, 'max_rows': 6}
FILTRO_LANCAMENTO = ["metr", "lancado", "lançado", "lancamento", "lançamento"]


# --- FUNÇÃO TELEGRAM (ASSINCRONA) ---
async def search_telegram_message(ta_number):
    try:
        async with TelegramClient(TELEGRAM_SESSION, TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            await client.get_dialogs()
            for group_id in TELEGRAM_GROUP_IDS:
                try:
                    entity = await client.get_entity(group_id)
                    async for message in client.iter_messages(entity, search=ta_number, limit=20):
                        if message.text:
                            return message.text
                except Exception:
                    continue
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return None
    return None


# --- ROTAS ---
@app.route('/buscar_telegram', methods=['POST'])
def buscar_telegram():
    data = request.get_json()
    ta = data.get('ta')
    if not ta: return jsonify({'error': 'Sem TA'}), 400

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        texto_encontrado = loop.run_until_complete(search_telegram_message(ta))
        loop.close()

        if texto_encontrado:
            return jsonify({'success': True, 'text': texto_encontrado})
        else:
            return jsonify({'success': False, 'message': 'TA não encontrada.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# ----------------------------
# FUNÇÕES DE BUSCA E FORMATAÇÃO
# ----------------------------
def buscar_endereco_gps(lat, lon):
    rua, numero, cidade, estado = "", "", "", "SP"

    # 1. Google Maps
    if GOOGLE_API_KEY:
        try:
            gmaps = GoogleV3(api_key=GOOGLE_API_KEY)
            location = gmaps.reverse(f"{lat}, {lon}", timeout=5)
            if location:
                best_res = location[0] if isinstance(location, list) else location
                if hasattr(best_res, 'raw'):
                    components = best_res.raw.get('address_components', [])
                    for comp in components:
                        if 'route' in comp['types']: rua = comp['long_name']
                        if 'street_number' in comp['types']: numero = comp['long_name']
                        if 'administrative_area_level_2' in comp['types']: cidade = comp['long_name']
                        if 'administrative_area_level_1' in comp['types']: estado = comp['short_name']
                if rua:
                    return (f"{rua}, {numero}" if numero else f"{rua}, S/N"), f"{cidade} - {estado}"
        except Exception as e:
            print(f"Erro Google Maps Address: {e}")

    # 2. ArcGIS
    try:
        geo_arc = ArcGIS(user_agent="sistema_croqui_tecnico_v1")
        loc_arc = geo_arc.reverse(f"{lat}, {lon}", timeout=5)
        if loc_arc and loc_arc.raw.get('address'):
            full_text = loc_arc.raw['address']
            parts = full_text.split(',')
            if len(parts) > 0: rua = parts[0].strip()
            if len(parts) > 1:
                possible_num = parts[1].strip()
                if re.match(r"^\d+(?:-\d+)?$", possible_num): numero = possible_num
            if not cidade and len(parts) >= 3: cidade = parts[-3].strip()
    except:
        pass

    # 3. Nominatim
    if not rua:
        try:
            geo_nom = Nominatim(user_agent="sistema_croqui_tecnico_v1")
            loc_nom = geo_nom.reverse(f"{lat}, {lon}", timeout=4)
            if loc_nom and hasattr(loc_nom, 'raw'):
                addr = loc_nom.raw.get('address', {})
                rua = addr.get('road', '') or addr.get('street', '')
                cidade = addr.get('city', '') or addr.get('town', '')
                numero = addr.get('house_number', '')
        except:
            pass

    end_parts = []
    if rua: end_parts.append(rua)
    if numero:
        end_parts.append(f", {numero}")
    elif rua:
        end_parts.append(", S/N")
    if not rua: return None, None
    return "".join(end_parts), f"{cidade} - {estado}" if cidade else ""


def formatar_texto(texto):
    if not texto: return ""
    texto = str(texto).strip().capitalize()
    siglas = ["SP", "MG", "RJ", "ES", "SC", "PR", "RS", "MS", "MT", "GO", "DF", "TO", "BA", "SE", "AL", "PE", "PB",
              "RN", "CE", "PI", "MA", "PA", "AP", "AM", "RR", "RO", "AC", "TA", "SGM", "CEO", "CTOP", "OTDR", "VT",
              "PP", "XC"]
    for sigla in siglas:
        pattern = re.compile(r'\b' + re.escape(sigla) + r'\b', re.IGNORECASE)
        texto = pattern.sub(sigla, texto)
    placas = re.findall(r'\b[a-zA-Z]{3}[-]?[0-9][a-zA-Z0-9][0-9]{2}\b', texto, re.IGNORECASE)
    for p in placas: texto = texto.replace(p, p.upper())
    return texto


def pct_to_pt(xpct, ypct, width_pt, height_pt): return xpct * width_pt, ypct * height_pt


# --- LÓGICA DE EXTRAÇÃO APRIMORADA ---
def extract_fields(text):
    data = {key: '' for key in
            ['ta', 'codigo_obra', 'causa', 'endereco', 'localidade', 'es', 'at', 'tronco', 'veiculo', 'data',
             'supervisor', 'lat', 'lon']}
    text = text.replace('\r\n', '\n').strip()

    # 1. TA e SGM
    m_ta = re.search(r"(?:TA|T\.A\.?|TICKET)\s*[:\-]?\s*\*?(\d{8,})\*?", text, re.IGNORECASE)
    if m_ta:
        data['ta'] = m_ta.group(1)
    else:
        # Tenta achar TA solta (35...)
        m_loose = re.search(r"\b(35\d{7})\b", text)
        if m_loose: data['ta'] = m_loose.group(1)

    m_sgm = re.search(r"(?:SGM|Obra)[\s:\-]*(\d{8,})", text, re.IGNORECASE)
    if m_sgm: data['codigo_obra'] = m_sgm.group(1)

    # 2. ES e AT (Prioridade para padrao "SOC.CR" ou "SOC.CR X ...")
    # A regra mais forte é 3 letras maiusculas + PONTO + 2 letras ou numeros
    m_sigla = re.search(r"\b([A-Z]{3})\.([A-Z0-9]{2})\b", text)
    if m_sigla:
        data['es'] = m_sigla.group(1).upper()
        data['at'] = m_sigla.group(2).upper()
    else:
        # Fallback antigo removido para evitar o erro do "23"
        pass

    # 3. TRONCO / CABO
    m_cabo = re.search(r"(?:NÚMERO DO CABO|CABO|TRONCO)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
    if m_cabo: data['tronco'] = m_cabo.group(1)

    # 4. DATA
    m_dt_cria = re.search(r"(?:DATA|CRIACAO).*?(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    if m_dt_cria:
        data['data'] = m_dt_cria.group(1)
    elif not data['data']:
        m_prev = re.search(r"Previs[ãa]o.*?(\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
        if m_prev:
            ymd = m_prev.group(1).split('-')
            data['data'] = f"{ymd[2]}/{ymd[1]}/{ymd[0]}"
        else:
            m_simple = re.search(r"(\d{2}/\d{2}/\d{4})", text)
            if m_simple: data['data'] = m_simple.group(1)

    # 5. Resto
    patterns = [(r"(?:causa|motivo)\s*[:;\-]?\s*(.+)", 'causa'),
                (r"(?:localidade|cidade)\s*[:;\-]?\s*(.+)", 'localidade'), (r"ve[ií]culo\s*[:;\-]?\s*(\S+)", 'veiculo')]
    for pat, key in patterns:
        if not data[key]:
            m = re.search(r"(?m)^.*?" + pat, text, re.IGNORECASE)
            if m: data[key] = m.group(1).strip().rstrip('.,;')

    match_gps = re.search(r"(-2\d\.\d+)[^\d\-]+(-4\d\.\d+)", text)
    if match_gps:
        data['lat'], data['lon'] = match_gps.group(1), match_gps.group(2)
        end_gps, loc_gps = buscar_endereco_gps(data['lat'], data['lon'])
        if end_gps:
            if not data['endereco'] or len(data['endereco']) < 5: data['endereco'] = end_gps
            if not data['localidade'] and loc_gps: data['localidade'] = loc_gps

    data['supervisor'] = "Wellington"

    # Executantes
    exec_list = []
    text_lower = text.lower()
    found = set()

    def try_add(term, official):
        if re.search(r"\b" + re.escape(term) + r"\b", text_lower):
            if official not in found:
                found.add(official)
                info = DB_TECNICOS.get(official)
                if info: exec_list.append({'name': official, 're': info['re']})

    for off in DB_TECNICOS: try_add(off, off)
    for alias, off in DB_ALIASES.items():
        if off not in found: try_add(alias, off)
    data['executantes_parsed'] = exec_list

    # Veiculo
    if not data['veiculo'] and exec_list:
        p = exec_list[0]['name']
        if p in DB_VEICULOS: data['veiculo'] = DB_VEICULOS[p]

    # Materiais
    raw_mat = ""
    m_gen = re.search(r"Ação de Recuperação:[\s\S]*?(?=\nMaterial|\nData|\Z|OBRA)", text, re.IGNORECASE)
    if m_gen: raw_mat = re.sub(r"Ação de Recuperação:\s*", "", m_gen.group(0), flags=re.IGNORECASE)
    if raw_mat:
        mat_lines = [l.strip() for l in raw_mat.splitlines() if l.strip()]
    else:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        tmp = []
        for l in lines:
            if re.match(r'^\d+[\s\w]', l) or any(
                    x in l.lower() for x in ['fusão', 'fusões', 'cabo', 'caixa', 'fita', 'tubo']):
                if "TA" not in l and "DATA" not in l and "OBRA" not in l: tmp.append(l)
        mat_lines = tmp

    return data, mat_lines


def detect_launch(material_lines):
    joined = " ".join(material_lines).lower()
    if "repuxad" in joined: return None
    patterns = [r"(\d{1,4})\s*(?:m\b|mt|mts|metr[ao]s?)", r"(\d{1,4})\s*(?:lan[cç]ad[oa]|lan[cç]amento)",
                r"(?:lan[cç]ad[oa]|lan[cç]amento)\s*(\d{1,4})"]
    for p in patterns:
        m = re.search(p, joined)
        if m: return int(m.group(1))
    return None


def detect_double_point(material_lines):
    joined = " ".join(material_lines).lower()
    if re.search(r"\b(?:02|2)\s*(?:reabertura|abertura|ceo|caixa|ctop|emenda)", joined): return True
    return False


def generate_pps(total_length, vt_each=15):
    usable = total_length - (2 * vt_each)
    if usable <= 0: return []
    num_spans = max(1, round(usable / 40))
    span_len = round(usable / num_spans)
    return [span_len] * num_spans


def dividir_tratativas(material_lines):
    divisiveis = ["fus", "fusão", "fusões", "fusao", "tubo", "loose"]
    especiais = ["ceo", "ptro", "abertura", "reabertura", "caixa"]
    p1, p2 = [], []
    itens = []
    for linha in material_lines:
        texto = linha.strip()
        low = texto.lower()
        m = re.match(r"(\d+)\s*[-xX]?\s*(.+)", low)
        if not m: itens.append({"qtd": 1, "nome": low, "orig": texto}); continue
        itens.append({"qtd": int(m.group(1)), "nome": m.group(2).strip(), "orig": texto})
    especiais_unitarios = [i for i in itens if i["qtd"] == 1 and any(k in i["nome"] for k in especiais)]
    if len(especiais_unitarios) == 2:
        p1.append(especiais_unitarios[0]["orig"]);
        p2.append(especiais_unitarios[1]["orig"])
        restantes = [i for i in itens if i not in especiais_unitarios]
    else:
        restantes = itens.copy()
    for item in restantes:
        qtd, nome, orig = item["qtd"], item["nome"], item["orig"]
        if any(f in nome for f in FILTRO_LANCAMENTO): p1.append(orig); continue
        if any(k in nome for k in especiais):
            if qtd == 1:
                p1.append(orig)
            else:
                metade = qtd // 2;
                resto = qtd - metade
                if metade > 0: p1.append(f"{metade} {nome}")
                if resto > 0: p2.append(f"{resto} {nome}")
            continue
        if any(k in nome for k in divisiveis):
            metade = qtd // 2;
            resto = qtd - metade
            if metade > 0: p1.append(f"{metade} {nome}")
            if resto > 0: p2.append(f"{resto} {nome}")
            continue
        p1.append(orig)
    return p1, p2


def create_overlay(parsed, materials_raw, pp_list, overlay_path):
    if not os.path.exists(TEMPLATE_PDF):
        width_pt, height_pt = 595.27, 841.89
    else:
        tpl = PdfReader(TEMPLATE_PDF);
        page0 = tpl.pages[0];
        media = page0.MediaBox
        llx, lly, urx, ury = map(float, media);
        width_pt = urx - llx;
        height_pt = ury - lly
    c = canvas.Canvas(str(overlay_path), pagesize=(width_pt, height_pt))

    def put_xy(key, text, size=9, manual_coords=None):
        if not text: return
        if manual_coords:
            xpct, ypct = manual_coords
        elif key in COORDS:
            xpct, ypct = COORDS[key]
        else:
            return
        x, y = pct_to_pt(xpct, ypct, width_pt, height_pt)
        c.setFont("Helvetica", size)
        lines = str(text).split('\n')
        for i, ln in enumerate(lines): c.drawString(x, y - (i * (size + 2)), ln)

    for key, val in parsed.items():
        if key not in ['executantes_parsed']: put_xy(key, val, size=9)
    execs = parsed.get('executantes_parsed', [])
    for i, item in enumerate(execs):
        if i >= EXEC_CONFIG['max_rows']: break
        current_y = EXEC_CONFIG['start_y'] - (i * EXEC_CONFIG['step_y'])
        put_xy(f"exec_{i}", item['name'].title(), size=9, manual_coords=(EXEC_CONFIG['name_x'], current_y))
        if item['re']: put_xy(f"re_{i}", item['re'], size=9, manual_coords=(EXEC_CONFIG['re_x'], current_y))
    mxp, myp = COORDS['materials_block']
    mx, my = pct_to_pt(mxp, myp, width_pt, height_pt)
    c.setFont('Helvetica', 8)
    for i, line in enumerate(materials_raw[:20]): c.drawString(mx, my - (i * 10), line)
    left_pct, bottom_pct, right_pct, top_pct = COORDS['croqui_rect']
    draw_y = height_pt * ((top_pct + bottom_pct) / 2)
    left_x = width_pt * (left_pct + 0.05);
    right_x = width_pt * (right_pct - 0.05)
    c.setLineWidth(2);
    c.setDash(4, 2);
    c.line(left_x, draw_y, right_x, draw_y);
    c.setDash([])
    if parsed.get('endereco'):
        addr = parsed['endereco']
        c.setFont('Helvetica-Bold', 10);
        tw = c.stringWidth(addr, 'Helvetica-Bold', 10)
        cx = (left_x + right_x) / 2;
        c.drawString(cx - (tw / 2), draw_y - 100, addr)
    if len(pp_list) == 0:
        total_width = right_x - left_x;
        mid_x = left_x + total_width / 2
        c.circle(left_x, draw_y, 4, fill=1);
        c.drawString(left_x - 12, draw_y - 20, "Início")
        c.circle(mid_x, draw_y, 4, fill=1);
        c.drawString(mid_x - 8, draw_y - 20, "XC")
        c.circle(right_x, draw_y, 4, fill=1);
        c.drawString(right_x - 8, draw_y - 20, "Fim")
        box_width, offset = 220, 35;
        box_height = 15 + 12 + (len(materials_raw) * 10)
        box_x = mid_x - (box_width / 2);
        box_y = draw_y + offset
        c.rect(box_x, box_y, box_width, box_height, fill=0)
        c.setFont("Helvetica-Bold", 8);
        c.drawString(box_x + 5, box_y + box_height - 10, "Tratativas")
        c.setFont("Helvetica", 8);
        text_start_y = box_y + box_height - 12 - 8
        for i, item in enumerate(materials_raw): c.drawString(box_x + 5, text_start_y - (i * 10), item)
        c.line(mid_x, draw_y, mid_x, box_y);
        c.drawString(mid_x - 4, box_y - 10, "↑")
    else:
        p1_list, p2_list = dividir_tratativas(materials_raw)
        offset, box_width = 30, 180
        h1 = 15 + 12 + (len(p1_list) * 10);
        bx1, by1 = left_x - 20, draw_y + offset
        c.rect(bx1, by1, box_width, h1, fill=0)
        c.setFont("Helvetica-Bold", 8);
        c.drawString(bx1 + 5, by1 + h1 - 10, "Tratativas E1")
        c.setFont("Helvetica", 8);
        tsy1 = by1 + h1 - 20
        for i, item in enumerate(p1_list): c.drawString(bx1 + 5, tsy1 - (i * 10), item)
        c.line(left_x, draw_y, bx1 + box_width / 2, by1)
        h2 = 15 + 12 + (len(p2_list) * 10);
        bx2, by2 = right_x - box_width + 20, draw_y + offset
        c.rect(bx2, by2, box_width, h2, fill=0)
        c.setFont("Helvetica-Bold", 8);
        c.drawString(bx2 + 5, by2 + h2 - 10, "Tratativas E2")
        c.setFont("Helvetica", 8);
        tsy2 = by2 + h2 - 20
        for i, item in enumerate(p2_list): c.drawString(bx2 + 5, tsy2 - (i * 10), item)
        c.line(right_x, draw_y, bx2 + box_width / 2, by2)
        total_width = right_x - left_x;
        step = total_width / len(pp_list);
        cur_x = left_x
        c.circle(cur_x, draw_y, 4, fill=1)
        has_cable = sum(pp_list) > 0
        if has_cable: c.drawString(cur_x - 10, draw_y + 15, "VT 15m")
        c.drawString(cur_x - 10, draw_y - 20, "XC Inicial")
        for i, dist in enumerate(pp_list):
            nxt_x = cur_x + step;
            mid = (cur_x + nxt_x) / 2
            if dist > 0 and has_cable: c.drawString(mid - 15, draw_y + 5, f"PP {dist}m")
            c.circle(nxt_x, draw_y, 4, fill=1)
            if i == len(pp_list) - 1:
                c.drawString(nxt_x - 10, draw_y - 20, "XC Final")
                if has_cable: c.drawString(nxt_x - 10, draw_y + 15, "VT 15m")
            else:
                c.drawString(nxt_x - 8, draw_y - 20, "XC")
            cur_x = nxt_x
    c.showPage();
    c.save()

def merge_overlay(overlay_path, out_path):
    if not os.path.exists(TEMPLATE_PDF): os.replace(overlay_path, out_path); return
    overlay = PdfReader(str(overlay_path));
    template = PdfReader(TEMPLATE_PDF)
    if len(template.pages) > 0 and len(overlay.pages) > 0:
        merger = PageMerge(template.pages[0]);
        merger.add(overlay.pages[0]).render()
    PdfWriter(str(out_path), trailer=template).write()


# --- HTML TEMPLATES ---
PASTE_HTML = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Colar Relatório</title><style>body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f0f2f5;padding:20px;text-align:center;margin:0}.container{width:90%;max-width:700px;margin:20px auto;background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1)}textarea{width:100%;height:300px;padding:15px;margin-bottom:20px;border:2px solid #ddd;border-radius:8px;font-size:16px;font-family:monospace;resize:vertical;background-color:#fafafa;box-sizing:border-box}textarea:focus{border-color:#007bff;outline:none;background:#fff}button{width:100%;padding:15px;font-size:18px;background:#007bff;color:#fff;border:none;border-radius:6px;cursor:pointer;transition:0.2s;font-weight:bold;margin-bottom:15px}button:hover{background:#0056b3}h2{color:#333;margin-bottom:10px}.manual-link{display:block;margin-top:15px;color:#666;text-decoration:none;font-size:16px}.manual-link:hover{text-decoration:underline;color:#007bff}.info{color:#666;font-size:14px;margin-bottom:20px}</style></head><body><div class="container"><h2>Gerador de Croquis</h2><p class="info">Cole abaixo o encerramento do <strong>GENESIS</strong>.</p><form method="post" action="/preencher"><textarea name="raw_text" placeholder="Cole aqui..."></textarea><br><button type="submit">Processar Texto &raquo;</button></form><a href="/form" class="manual-link">Preencher manualmente</a></div></body></html>"""

FORM_HTML = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Confirmar</title><style>body{font-family:'Segoe UI',sans-serif;background:#f0f2f5;padding:10px;margin:0}.container{width:95%;max-width:900px;margin:10px auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.05);box-sizing:border-box}input,textarea{width:100%;padding:12px;margin-bottom:15px;border:1px solid #ccc;border-radius:5px;font-size:16px;box-sizing:border-box}textarea{height:150px;font-family:monospace}button{padding:15px;font-size:16px;border:none;border-radius:5px;cursor:pointer;font-weight:bold;color:#fff;width:100%;margin-bottom:10px}#btn-validate{background:#28a745}#btn-validate:hover{background:#218838}h3{margin-top:20px;border-bottom:2px solid #eee;padding-bottom:10px;color:#444;font-size:18px}label{font-weight:600;font-size:14px;color:#555;display:block;margin-bottom:5px}.error{border:2px solid #dc3545!important;background:#fff0f0}.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:15px}.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:15px}@media(max-width:768px){.grid-2,.grid-3{grid-template-columns:1fr;gap:10px}.container{padding:15px;width:100%}}.modal-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:999;display:none;justify-content:center;align-items:center}.modal-content{background:#fff;padding:25px;border-radius:12px;width:90%;max-width:400px;box-shadow:0 5px 15px rgba(0,0,0,0.3)}.modal-title{font-size:1.2rem;font-weight:bold;margin-bottom:15px;color:#dc3545}.modal-list{margin-bottom:20px;padding-left:20px;color:#333}.modal-actions{display:flex;flex-direction:column;gap:10px}#btn-modal-back{background:#6c757d}#btn-modal-proceed{background:#007bff}.tag{display:inline-block;background:#e9ecef;color:#333;padding:8px 14px;border-radius:20px;margin:4px;font-size:14px;border:1px solid #ddd}.tag span{margin-left:10px;cursor:pointer;color:#dc3545;font-weight:bold}#exec-list{max-height:200px;overflow-y:auto;border:1px solid #eee;border-radius:4px;margin-bottom:10px}#exec-list div{padding:12px;border-bottom:1px solid #f0f0f0;cursor:pointer;display:flex;justify-content:space-between}#exec-list div:hover{background:#f8f9fa;color:#007bff}.area-badge{color:#999;font-size:0.9em}.back-btn{background:#007bff;text-decoration:none;display:block;color:white;padding:15px;border-radius:5px;text-align:center;margin-bottom:10px;font-weight:bold}</style></head><script>document.addEventListener('DOMContentLoaded',()=>{let tecnicos=[];let selecionados={{ executantes_list|tojson }};let veiculosMap={{ veiculos_map|tojson }};fetch('/tecnicos').then(r=>r.json()).then(d=>tecnicos=d);const form=document.querySelector('form');const input=document.getElementById('exec-input');const list=document.getElementById('exec-list');const hidden=document.getElementById('exec-hidden');const tagsBox=document.getElementById('exec-tags');const inputVeiculo=document.querySelector('input[name="veiculo"]');const modalOverlay=document.getElementById('modal-overlay');const modalList=document.getElementById('modal-list');const btnValidate=document.getElementById('btn-validate');const btnModalBack=document.getElementById('btn-modal-back');const btnModalProceed=document.getElementById('btn-modal-proceed');function atualizarHidden(){hidden.value=selecionados.join(', ');if(selecionados.length>0)input.classList.remove('error')}function renderTags(){tagsBox.innerHTML='';selecionados.forEach(nome=>{const tag=document.createElement('div');tag.className='tag';tag.innerHTML=`${nome} <span>&times;</span>`;tag.querySelector('span').onclick=()=>{selecionados=selecionados.filter(n=>n!==nome);atualizarHidden();renderTags()};tagsBox.appendChild(tag)})}renderTags();atualizarHidden();input.addEventListener('input',()=>{const v=input.value.toLowerCase();list.innerHTML='';if(!v)return;input.classList.remove('error');tecnicos.filter(t=>t.name.toLowerCase().includes(v)&&!selecionados.includes(t.name)).slice(0,8).forEach(t=>{const div=document.createElement('div');div.innerHTML=`<span>${t.name}</span> <span class="area-badge">Area ${t.area}</span>`;div.onclick=()=>{selecionados.push(t.name);if(veiculosMap[t.name]&&inputVeiculo.value==="")inputVeiculo.value=veiculosMap[t.name];inputVeiculo.classList.remove('error');atualizarHidden();renderTags();input.value='';list.innerHTML=''};list.appendChild(div)})});document.querySelectorAll('input, textarea').forEach(el=>{el.addEventListener('input',function(){if(this.value.trim()!=='')this.classList.remove('error')})});btnValidate.addEventListener('click',(e)=>{e.preventDefault();let missing=[];const fields=[{name:'ta',label:'TA'},{name:'codigo_obra',label:'Código Obra'},{name:'causa',label:'Causa'},{name:'endereco',label:'Endereço'},{name:'localidade',label:'Localidade'},{name:'tronco',label:'Tronco'},{name:'veiculo',label:'Veículo'},{name:'supervisor',label:'Supervisor'},{name:'data',label:'Data'},{name:'itens',label:'Tratativas'}];fields.forEach(f=>{const el=document.querySelector(`[name="${f.name}"]`);if(!el.value.trim()){el.classList.add('error');missing.push(f.label)}});if(selecionados.length===0){input.classList.add('error');missing.push('Executantes')}if(missing.length>0){modalList.innerHTML=missing.map(i=>`<li>${i}</li>`).join('');modalOverlay.style.display='flex'}else{form.submit()}});btnModalBack.addEventListener('click',()=>{modalOverlay.style.display='none'});btnModalProceed.addEventListener('click',()=>{modalOverlay.style.display='none';form.submit()})});</script><body><div id="modal-overlay" class="modal-overlay"><div class="modal-content"><div class="modal-title">Campos Vazios</div><p>Faltam preencher:</p><ul id="modal-list" class="modal-list"></ul><div class="modal-actions"><button id="btn-modal-back" type="button">Voltar</button><button id="btn-modal-proceed" type="button">Gerar Assim Mesmo</button></div></div></div><div class="container"><form method="post" action="/generate" target="_blank"><input type="hidden" name="lat" value="{{ data.get('lat','') }}"><input type="hidden" name="lon" value="{{ data.get('lon','') }}"><h3>Dados Principais</h3><div class="grid-2"><div><label>TA</label><input name="ta" value="{{ data.get('ta','') }}"></div><div><label>Código Obra (SGM)</label><input name="codigo_obra" value="{{ data.get('codigo_obra','') }}"></div></div><label>Causa</label><input name="causa" value="{{ data.get('causa','') }}"><label>Endereço</label><input name="endereco" value="{{ data.get('endereco','') }}"><div class="grid-3"><div><label>Localidade</label><input name="localidade" value="{{ data.get('localidade','') }}"></div><div><label>ES</label><input name="es" value="{{ data.get('es','') }}"></div><div><label>AT</label><input name="at" value="{{ data.get('at','') }}"></div></div><div class="grid-2"><div><label>Tronco</label><input name="tronco" value="{{ data.get('tronco','') }}"></div><div><label>Veículo</label><input name="veiculo" value="{{ data.get('veiculo','') }}"></div></div><div class="grid-2"><div><label>Supervisor</label><input name="supervisor" value="{{ data.get('supervisor','Wellington') }}"></div><div><label>Data</label><input name="data" value="{{ data.get('data','') }}"></div></div><h3>Executantes</h3><div id="exec-tags" style="margin-bottom:10px"></div><input id="exec-input" placeholder="Buscar técnico..."><div id="exec-list"></div><input type="hidden" name="executantes" id="exec-hidden"><h3>Tratativas</h3><textarea name="itens">{{ itens_texto }}</textarea><div style="margin-top:30px"><button id="btn-validate" type="submit">Gerar PDF</button><a href="/" class="back-btn">Voltar</a></div></form></div></body></html>"""


# --- ROTAS ---
@app.route('/')
def index(): return render_template_string(PASTE_HTML)


@app.route('/tecnicos')
def tecnicos(): return json.dumps([{'name': k, 'area': v.get('area', '')} for k, v in DB_TECNICOS.items()])


@app.route('/form')
def form_vazio(): return render_template_string(FORM_HTML, data={}, itens_texto="", executantes_list=[],
                                                veiculos_map=DB_VEICULOS)


# --- NOVA LÓGICA DE PREENCHIMENTO (MERGE) ---
@app.route('/preencher', methods=['POST'])
def preencher():
    raw_text = request.form.get('raw_text', '')
    parsed_manual, material_lines = extract_fields(raw_text)

    ta_encontrada = parsed_manual.get('ta')
    if ta_encontrada:
        print(f"Buscando complemento no Telegram para TA: {ta_encontrada}")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            texto_telegram = loop.run_until_complete(search_telegram_message(ta_encontrada))
            loop.close()

            if texto_telegram:
                print("Texto encontrado! Mesclando...")
                parsed_telegram, _ = extract_fields(texto_telegram)
                # Mescla inteligente: só preenche o que falta
                for campo in ['es', 'at', 'tronco', 'data']:
                    if not parsed_manual[campo] and parsed_telegram[campo]:
                        parsed_manual[campo] = parsed_telegram[campo]
        except Exception as e:
            print(f"Erro ao buscar no Telegram: {e}")

    exec_names = [e['name'].title() for e in parsed_manual.get('executantes_parsed', [])]
    itens_texto = "\n".join(material_lines)
    return render_template_string(FORM_HTML, data=parsed_manual, itens_texto=itens_texto, executantes_list=exec_names,
                                  veiculos_map=DB_VEICULOS)


@app.route('/view/<filename>')
def view_pdf(filename): return redirect(url_for('outputs', filename=filename))


@app.route('/outputs/<path:filename>')
def outputs(filename): return send_from_directory(OUTPUT_DIR, filename)


@app.route('/generate', methods=['POST'])
def generate():
    execs_string = request.form.get('executantes', '')
    exec_list = []
    if execs_string:
        for nome in execs_string.split(','):
            clean = nome.strip().lower()
            if clean in DB_TECNICOS:
                re_code = DB_TECNICOS[clean].get('re', '')
                parts = clean.split()
                if len(parts) > 1:
                    short_name = f"{parts[0].capitalize()} {parts[-1].capitalize()}"
                else:
                    short_name = clean.capitalize()
                exec_list.append({'name': short_name, 're': re_code})
            else:
                exec_list.append({'name': clean.title(), 're': ''})

    parsed = {
        'ta': request.form.get('ta', ''), 'codigo_obra': request.form.get('codigo_obra', ''),
        'causa': request.form.get('causa', ''), 'endereco': request.form.get('endereco', ''),
        'localidade': request.form.get('localidade', ''), 'es': request.form.get('es', ''),
        'at': request.form.get('at', ''), 'tronco': request.form.get('tronco', ''),
        'veiculo': request.form.get('veiculo', ''), 'data': request.form.get('data', ''),
        'supervisor': request.form.get('supervisor', ''), 'executantes_parsed': exec_list,
        'lat': request.form.get('lat', ''), 'lon': request.form.get('lon', '')
    }

    itens_raw = request.form.get('itens', '')
    for k in ['causa', 'endereco', 'localidade', 'veiculo', 'supervisor']: parsed[k] = formatar_texto(parsed[k])
    material_lines = [formatar_texto(l.strip()) for l in itens_raw.splitlines() if l.strip()]

    total_len = detect_launch(material_lines)
    is_double_point = False
    if total_len is None:
        if detect_double_point(material_lines): is_double_point = True; total_len = 0
    pp_list = []
    if total_len is not None:
        if total_len > 0:
            pp_list = generate_pps(total_len)
        elif is_double_point:
            pp_list = [0, 0, 0, 0]

    codigo = parsed.get('ta') or f"doc_{random.randint(1000, 9999)}"
    codigo = re.sub(r'[^\w\-]', '', codigo)

    overlay_path = OUTPUT_DIR / f"{codigo}_overlay.pdf"
    out_pdf = OUTPUT_DIR / f"{codigo}.pdf"
    create_overlay(parsed, material_lines, pp_list, overlay_path)
    merge_overlay(overlay_path, out_pdf)
    return redirect(url_for('view_pdf', filename=out_pdf.name))


if __name__ == '__main__':
    if not os.path.exists(TEMPLATE_PDF):
        c = canvas.Canvas(TEMPLATE_PDF);
        c.drawString(100, 700, "TEMPLATE AUSENTE");
        c.save()
    app.run(debug=True, port=5000)
