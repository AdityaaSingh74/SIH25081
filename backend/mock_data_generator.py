import random
import json

def generate_train(i):
    mileage = random.randint(15000,45000)
    certDays = random.randint(1,30)
    openJobs = random.randint(0,5)
    jobCritical = random.random() < 0.2
    branding = {'required':8, 'served': random.randint(0,12)} if random.random() < 0.6 else None
    failureRisk = round(random.random() * 0.3 + (openJobs * 0.08) + (0.3 if certDays<3 else 0), 3)
    return {
        'id': f'TS-{i:02d}',
        'depot': random.choice(['Aluva','Palarivattom','Thevara']),
        'mileage': mileage,
        'certDays': certDays,
        'openJobs': openJobs,
        'jobCritical': jobCritical,
        'branding': branding,
        'cleaningOverrun': random.randint(0,90),
        'failureRisk': failureRisk
    }

if __name__ == '__main__':
    trains = [generate_train(i+1) for i in range(25)]
    print(json.dumps({'trains':trains}, indent=2))
