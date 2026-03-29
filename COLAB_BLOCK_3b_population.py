# БЛОК 3б — підрахунок населення (Kontur Population 2023)
import math, os, gzip, io

POP_URL  = "https://github.com/kirdanova14/tc-dashboard/raw/main/population_UA.csv.gz"
POP_PATH = "/content/population_UA.csv.gz"

if not os.path.exists(POP_PATH):
    print("📥 Завантаження даних населення (~2 МБ)...")
    import requests as req
    r = req.get(POP_URL, stream=True)
    with open(POP_PATH, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Файл завантажено!")
else:
    print("✅ Файл вже є в кеші")

# Завантажити всі точки в пам'ять
print("📊 Читання даних...", end=' ')
pop_points = []
with gzip.open(POP_PATH, 'rt', encoding='utf-8') as f:
    next(f)  # skip header
    for line in f:
        parts = line.strip().split(',')
        if len(parts) == 3:
            pop_points.append((float(parts[0]), float(parts[1]), int(parts[2])))
print(f"{len(pop_points):,} шестикутників")

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def count_population(lat, lon, r_walk_km, r_car_km):
    lat_d = r_car_km / 111.0
    lon_d = r_car_km / (111.0 * math.cos(math.radians(lat)))
    pop_walk = pop_car = 0
    for glat, glon, pop in pop_points:
        # Швидкий bbox фільтр
        if not (lat-lat_d <= glat <= lat+lat_d and lon-lon_d <= glon <= lon+lon_d):
            continue
        dist = haversine_km(lat, lon, glat, glon)
        if dist <= r_car_km:
            pop_car += pop
            if dist <= r_walk_km:
                pop_walk += pop
    return int(pop_walk), int(pop_car)

print("\n👥 Підрахунок населення...")
r_walk = RADIUS_WALK / 1000
r_car  = RADIUS_CAR  / 1000

for loc in LOCATIONS:
    pw, pc = count_population(loc['lat'], loc['lon'], r_walk, r_car)
    print(f"  📍 {loc['name']}: 👣 {pw:,} осіб ({RADIUS_WALK}м) | 🚗 {pc:,} осіб ({RADIUS_CAR}м)")
    if loc['name'] in output:
        output[loc['name']]['population_walk'] = pw
        output[loc['name']]['population_car']  = pc

# Оновити JSON файл
with open("popular_times.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\n✅ Дані населення додано до файлу!")
