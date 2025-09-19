import pandas as pd

def parse_maximo_csv(path: str):
    df = pd.read_csv(path)
    out = []
    for _, row in df.iterrows():
        t = {
            'id': row.get('TrainID'),
            'mileage': int(row.get('Mileage_km', 0)),
            'certDays': int(row.get('CertDaysLeft', 0)),
            'openJobs': int(row.get('OpenJobCount', 0)),
            'branding': {'required':8, 'served': int(row.get('BrandingServedHours', 0))}
        }
        out.append(t)
    return out
