"""
Скрипт для проверки силовых тренировок конкретного пользователя

Использование:
    python check_user_strength_workouts.py user@email.com

Для Docker:
    docker exec backend python check_user_strength_workouts.py user@email.com /app/data/triplan.db
"""
import sqlite3
import sys
from datetime import date

def check_user_strength(email, db_path='./triplan.db'):
    """Проверяет силовые тренировки для конкретного пользователя"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print('=' * 70)
    print(f'DIAGNOSTIKA POL\'ZOVATELYA: {email}')
    print('=' * 70)

    # 1. Находим пользователя
    cursor.execute('SELECT id, email, has_strength_training, updated_at FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if not user:
        print(f'\n[ERROR] Pol\'zovatel\' ne najden: {email}')
        conn.close()
        return False

    user_id, user_email, has_strength, user_updated = user
    print(f'\n[1] POL\'ZOVATEL\':')
    print(f'    ID: {user_id}')
    print(f'    Email: {user_email}')
    print(f'    has_strength_training: {\"ON\" if has_strength == 1 else \"OFF\"}')
    print(f'    updated_at: {user_updated}')

    if has_strength != 1:
        print('\n[!] PROBLEMA: has_strength_training = OFF')
        print('    RESHENIE: Vklyuchite nastrojku v Profile')
        conn.close()
        return False

    # 2. Проверяем план
    cursor.execute('''
        SELECT id, competition_date, complexity, created_at
        FROM training_plans
        WHERE user_id = ?
    ''', (user_id,))
    plan = cursor.fetchone()

    if not plan:
        print('\n[!] PROBLEMA: U pol\'zovatelya NET plana')
        print('    RESHENIE: Sozda te plan v Profile')
        conn.close()
        return False

    plan_id, comp_date, complexity, plan_created = plan
    print(f'\n[2] PLAN:')
    print(f'    ID: {plan_id}')
    print(f'    Data sorevnovaniya: {comp_date}')
    print(f'    Slozhnost\': {complexity}')
    print(f'    created_at: {plan_created}')

    # Проверяем время создания
    if plan_created < user_updated:
        print('\n[!] PROBLEMA: Plan sozdan DO vklyucheniya nastrojki!')
        print(f'    Plan sozdan: {plan_created}')
        print(f'    Nastrojka vklyuchena: {user_updated}')
        print('    RESHENIE: Peresozdajte plan (Profile -> Izmenit\' plan)')
        conn.close()
        return False

    # 3. Считаем тренировки
    cursor.execute('SELECT COUNT(*) FROM workouts WHERE plan_id = ?', (plan_id,))
    total_workouts = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM workouts
        WHERE plan_id = ? AND LOWER(sport_type) = 'strength'
    ''', (plan_id,))
    strength_workouts = cursor.fetchone()[0]

    print(f'\n[3] TRENIROVKI:')
    print(f'    Vsego: {total_workouts}')
    print(f'    Silovyh: {strength_workouts}')

    if strength_workouts == 0:
        print('\n[!] PROBLEMA: Silovye trenirovki NE sozdany!')

        # Проверяем недели до соревнования
        try:
            comp_date_obj = date.fromisoformat(comp_date)
            days_to_comp = (comp_date_obj - date.today()).days
            weeks_to_comp = days_to_comp // 7
            print(f'    Nedel\' do sorevnovaniya: {weeks_to_comp}')

            if weeks_to_comp < 8:
                print('    PRICHINA: Do sorevnovaniya men\'she 8 nedel\'')
                print('    Silovye trenirovki dobavlyayutsya tol\'ko v fazy base/build')
            else:
                print('    PRICHINA: Neizvestnaya problema')
                print('    RESHENIE: Peresozdajte plan')
        except:
            pass

        conn.close()
        return False

    # 4. Показываем примеры силовых тренировок
    cursor.execute('''
        SELECT id, date, duration_minutes
        FROM workouts
        WHERE plan_id = ? AND LOWER(sport_type) = 'strength'
        ORDER BY date
        LIMIT 5
    ''', (plan_id,))
    strength_list = cursor.fetchall()

    print(f'\n[4] PRIMERY SILOVYH TRENIROVOK:')
    for w in strength_list:
        print(f'    ID: {w[0]}, Data: {w[1]}, Dlitel\'nost\': {w[2]} min')

    print('\n' + '=' * 70)
    print('[SUCCESS] Silovye trenirovki prisutstvuyut v plane!')
    print('=' * 70)

    conn.close()
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Ispol\'zovanie:')
        print('  python check_user_strength_workouts.py user@email.com')
        print('  python check_user_strength_workouts.py user@email.com /path/to/triplan.db')
        sys.exit(1)

    email = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else './triplan.db'

    success = check_user_strength(email, db_path)
    sys.exit(0 if success else 1)
