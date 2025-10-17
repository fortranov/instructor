@echo off
chcp 65001 >nul
REM Скрипт для очистки Docker ресурсов в Windows

echo ==========================================
echo Очистка Docker ресурсов
echo ==========================================
echo.

REM Показываем текущее использование Docker
echo Текущее использование Docker:
docker system df
echo.

REM Спрашиваем подтверждение
set /p confirm="Вы хотите очистить неиспользуемые Docker ресурсы? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo Останавливаем контейнеры...
    docker-compose down
    
    echo.
    echo Удаляем остановленные контейнеры...
    docker container prune -f
    
    echo.
    echo Удаляем неиспользуемые образы...
    docker image prune -a -f
    
    echo.
    echo Удаляем неиспользуемые volumes...
    docker volume prune -f
    
    echo.
    echo Очищаем build cache...
    docker builder prune -a -f
    
    echo.
    echo ==========================================
    echo Очистка завершена!
    echo ==========================================
    echo.
    
    echo Новое использование Docker:
    docker system df
    echo.
    
    echo Рекомендация: Теперь можете запустить сборку проекта
    echo docker-compose build --no-cache
) else (
    echo Очистка отменена.
)

pause

