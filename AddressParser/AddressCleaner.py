import re

sub_dict = {
    "VN": "VIET NAM ",
    "H": "HUYEN ",
    "HCM": "HO CHI MINH ",
    "TP": "THANH PHO ",
    "P": "PHUONG ",
    "P.": "PHUONG ",
    "TT": "THI TRAN ",
    "Q": "QUAN ",
    "TPHCM": "THANH PHO HO CHI MINH ",
    "TX": "THI XA ",
    "KP": "KHU PHO ",
    "Q.": "QUAN ",
    "TP.": "THANH PHO ",
    "CC": "CHUNG CU ",
    "TDP": "TO DAN PHO ",
    "BHH": "BINH HUNG HOA ",
    "KDC": "KHU DAN CU ",
    "GV": "GO VAP ",
    "BTAN": "BINH TAN ",
    "KG": "KIEN GIANG ",
    "H.": "HUYEN ",
    "CMT8": "CACH MANG THANG TAM ",
    "HN": "HA NOI ",
    "KCN": "KHU CONG NGHIEP ",
    "BRVT": "BA RIA - VUNG TAU ",
    "BTHANH": "BINH THANH ",
    "X": "XA ",
    "X.": "XA ",
    "BC": "BINH CHANH ",
    "DS": "DUONG SO ",
    "TX.": "THI XA ",
    "DHT": "DONG HUNG THUAN ",
    "NK": "NINH KIEU ",
    "KTX": "KY TUC XA ",
    "TT.": "THI TRAN ",
    "CX": "CU XA ",
    "D.": "",
    "QTB": "QUAN TAN BINH ",
    "C/C": "CHUNG CU ",
    "BHHB": "BINH HUNG HOA B ",
    "BMT": "BUON MA THUOT ",
    "HBC": "HIEP BINH CHANH ",
    "QL1A": "QUOC LO 1A ",
    "DSO": "SO ",
    "QL": "QUOC LO ",
    "KDT": "KHU DO THI ",
    "TCH": "TAN CHANH HIEP ",
    "XVNT": "XO VIET NGHE TINH ",
    "PN": "PHU NHUAN ",
    "VLA": "VINH LOC A ",
    "VLB": "VINH LOC B ",
    "HBP": "HIEP BINH PHUOC ",
    "XM": "XOM MOI ",
    "QL13": "QUOC LO 13 ",
    "LK": "LIEN KHU ",
    "CTY": "CONG TY ",
    "TNP": "TANG NHON PHU ",
    "TL": "TINH LO ",
    "QTAN": "QUAN TAN ",
    "KP.": "KHU PHO ",
    "TPCT": "THANH PHO CAN THO ",
    "TPCL": "THANH PHO CAO LANH ",
    "THT": "TAN HUNG THUAN ",
    "TMT": "TRUNG MY TAY ",
    "BCHANH": "BINH CHANH ",
    "TPHU": "TAN PHU ",
    "THPT": "TRUNG HOC PHO THONG ",
    "THCHAM": "THAP CHAM ",
    "PHRANG": "PHAN RANG ",
    "TG": "TIEN GIANG ",
    "TTAO": "TAN TAO ",
    "HBT": "HAI BA TRUNG ",
    "SN": "SO NHA "
}

pattern = re.compile(r'(?:[A-z]+\.)+|[^\|\s\,\-\(\)\'\&]+')

BANG_XOA_DAU_FULL = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5,
    chr(774) + chr(770) + chr(795) + chr(769) + chr(768) + chr(777) + chr(771) + chr(803) # 8 kí tự dấu dưới dạng unicode chuẩn D
)

def strip_accents(txt:str) -> str:
    txt = txt.strip()
    return txt.translate(BANG_XOA_DAU_FULL)


def sub_acronym(matchobj:re.Match) -> str:
    word = matchobj.group(0).upper()
    if word in sub_dict:
        return sub_dict.get(word)
    else:
        # deal with cases like KP1, KV12, P12, Q1, LK9
        result = re.sub(r'KV(\d{1,2})', r'KHU VUC \1', word)
        result = re.sub(r'KP(\d{1,2})', r'KHU PHO \1', result)
        result = re.sub(r'Q(\d{1,2})', r'QUAN \1', result)
        result = re.sub(r'P(\d{1,2})', r'PHUONG \1', result)
        result = re.sub(r'LK(\d{1,2})', r'LIEN KHU \1', result)
        return result


def clean_common_numeric_acronym(input:str) -> str:
    word = input.upper()
    result = re.sub(r'KV\s*\.\s*(\d{1,2})', r'KHU VUC \1', word)
    result = re.sub(r'KP\s*\.\s*(\d{1,2})', r'KHU PHO \1', result)
    result = re.sub(r'Q\s*\.\s*(\d{1,2})', r'QUAN \1', result)
    result = re.sub(r'P\s*\.\s*(\d{1,2})', r'PHUONG \1', result)
    result = re.sub(r'LK\s*\.\s*(\d{1,3})', r'LIEN KHU \1', result)
    return result


def clean_acronym(input:str) -> str:
    input = strip_accents(input.upper())
    replaced_acronym = pattern.sub(sub_acronym, clean_common_numeric_acronym(input))
    return re.sub(r'[\s\|\,]{1,}', ' ', replaced_acronym)


def overlapping_substrings(input:str, n:int) -> list[str]:
    tokens = input.split()
    chunks = [(' '.join(tokens[i:i+n]), (i, i+n-1)) for i in range(len(tokens)-n+1)]
    return chunks


def split_to_chunks(input:str, chunk_size_min=2, chunk_size_max=5) -> list[list[str]]:
    cleaned = clean_acronym(input)
    result = []
    for i in range(chunk_size_max + 1 - chunk_size_min):
        result.extend(overlapping_substrings(cleaned, chunk_size_min + i))
        # result.reverse()
    return result


