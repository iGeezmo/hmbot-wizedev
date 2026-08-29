#!/usr/bin/env python3
"""
Tool policy — классификация инструментов по уровню риска.
По мотивам Odysseus: src/tool_policy.py, src/tool_approval_scopes.py, src/tool_security.py

Уровни:
- READ     — безопасно, только чтение (нет побочных эффектов)
- WRITE    — изменения, но обратимые (файлы, заметки, письма)
- DESTRUCTIVE — необратимые операции (удаление, отправка, деплой, оплата)

Каждый tool имеет:
- level: READ | WRITE | DESTRUCTIVE
- requires_approval: bool (по умолчанию True для DESTRUCTIVE)
- description: что делает
- category: groups для batch operations
"""
import json
from pathlib import Path

POLICY_FILE = Path('/root/.hermes/tool_policy.json')

# Классификация инструментов Hermes + MCP matrix
TOOL_POLICY = {
    # === READ (безопасно) ===
    'read_file': {'level': 'READ', 'category': 'filesystem', 'description': 'Читает текстовый файл'},
    'search_files': {'level': 'READ', 'category': 'filesystem', 'description': 'Поиск по содержимому/именам'},
    'list_directory': {'level': 'READ', 'category': 'filesystem', 'description': 'Список файлов'},
    'web_search': {'level': 'READ', 'category': 'web', 'description': 'Поиск в интернете'},
    'extract_content_from_websites': {'level': 'READ', 'category': 'web', 'description': 'Извлечение контента с URL'},
    'get_voice_list': {'level': 'READ', 'category': 'media', 'description': 'Список голосов TTS'},
    'images_list': {'level': 'READ', 'category': 'media', 'description': 'Список картинок'},
    'images_understand': {'level': 'READ', 'category': 'media', 'description': 'OCR/описание картинки'},
    'listen_audio': {'level': 'READ', 'category': 'media', 'description': 'Анализ аудио'},
    'audios_understand': {'level': 'READ', 'category': 'media', 'description': 'Транскрипция/анализ'},
    'videos_understand': {'level': 'READ', 'category': 'media', 'description': 'Анализ видео'},
    'session_search': {'level': 'READ', 'category': 'memory', 'description': 'Поиск по прошлым сессиям'},
    'skills_list': {'level': 'READ', 'category': 'memory', 'description': 'Список скиллов'},
    'skill_view': {'level': 'READ', 'category': 'memory', 'description': 'Содержимое скилла'},
    'todos': {'level': 'READ', 'category': 'agent', 'description': 'Список задач (read-only если не задан todos)'},
    'process_list': {'level': 'READ', 'category': 'system', 'description': 'Список фоновых процессов'},

    # === WRITE (обратимые изменения) ===
    'write_file': {'level': 'WRITE', 'category': 'filesystem', 'description': 'Создаёт/перезаписывает файл',
                   'notes': 'OVERWRITE — не merge'},
    'patch': {'level': 'WRITE', 'category': 'filesystem', 'description': 'Точечная правка файла',
              'notes': 'Безопаснее write_file'},
    'memory': {'level': 'WRITE', 'category': 'memory', 'description': 'Сохраняет в долговременную память'},
    'skill_manage_create': {'level': 'WRITE', 'category': 'memory', 'description': 'Создаёт скилл'},
    'skill_manage_patch': {'level': 'WRITE', 'category': 'memory', 'description': 'Обновляет скилл'},
    'skill_manage_edit': {'level': 'WRITE', 'category': 'memory', 'description': 'Перезаписывает скилл'},
    'cronjob_create': {'level': 'WRITE', 'category': 'agent', 'description': 'Создаёт cron-задачу',
                       'notes': 'Будет работать в фоне автоматически'},
    'cronjob_update': {'level': 'WRITE', 'category': 'agent', 'description': 'Обновляет cron-задачу'},
    'todo_set': {'level': 'WRITE', 'category': 'agent', 'description': 'Обновляет список задач сессии'},
    'image_synthesize': {'level': 'WRITE', 'category': 'media', 'description': 'Генерирует картинку (стоимость API)'},
    'synthesize_speech': {'level': 'WRITE', 'category': 'media', 'description': 'TTS генерация (стоимость API)'},
    'text_to_music': {'level': 'WRITE', 'category': 'media', 'description': 'Генерация музыки (стоимость API)'},
    'gen_videos': {'level': 'WRITE', 'category': 'media', 'description': 'Генерация видео (стоимость API)'},
    'execute_code': {'level': 'WRITE', 'category': 'system', 'description': 'Запускает Python',
                     'notes': 'Сложно отменить; sandbox timeout 5 мин'},

    # === DESTRUCTIVE (требует одобрения) ===
    'skill_manage_delete': {'level': 'DESTRUCTIVE', 'category': 'memory', 'requires_approval': True,
                            'description': 'Удаляет скилл'},
    'cronjob_remove': {'level': 'DESTRUCTIVE', 'category': 'agent', 'requires_approval': True,
                       'description': 'Удаляет cron-задачу'},
    'process_kill': {'level': 'DESTRUCTIVE', 'category': 'system', 'requires_approval': True,
                     'description': 'Убивает фоновый процесс'},
    'process_close': {'level': 'DESTRUCTIVE', 'category': 'system', 'requires_approval': False,
                      'description': 'Закрывает stdin процесса (безопасно)'},
    'terminal': {'level': 'DESTRUCTIVE', 'category': 'system', 'requires_approval': False,
                 'description': 'Shell-команда',
                 'notes': 'Уровень зависит от команды. read-only команды безопасны, rm/deploy — деструктивны'},
    'delegate_task': {'level': 'DESTRUCTIVE', 'category': 'agent', 'requires_approval': False,
                      'description': 'Спавнит subagent (расходует ресурсы)'},
    'send_message': {'level': 'DESTRUCTIVE', 'category': 'comms', 'requires_approval': True,
                     'description': 'Отправляет сообщение в мессенджер (необратимо)'},
    'deploy': {'level': 'DESTRUCTIVE', 'category': 'web', 'requires_approval': True,
               'description': 'Деплой на web-сервер (публично доступен)'},
    'upload_to_cdn': {'level': 'WRITE', 'category': 'web', 'description': 'Загружает файл в CDN (публичная ссылка)'},
}


# Команды которые считаются деструктивными даже в shell
DESTRUCTIVE_SHELL_PATTERNS = [
    r'\brm\s+(-[a-z]*)?\s*-?[rf]',  # rm -rf
    r'\bdd\s+',
    r'\bmkfs\.',
    r'\bformat\s',
    r'\bshutdown\b',
    r'\breboot\b',
    r'\bkill\s+-9\s+1\b',  # kill init
    r'>\s*/etc/',  # перезапись /etc
    r'\bchmod\s+(-R\s+)?000\s+/',  # chmod 000 на /
    r'\bapt(-get)?\s+(remove|purge| autoremove)',
    r'\bgit\s+push\s+.*--force\b',
    r'\bgit\s+push\s+-f\b',
    r'\bcurl\s+.*\|\s*bash',  # pipe curl to bash
    r'\bcurl\s+.*\|\s*sh',
    r'\bwget\s+.*\|\s*bash',
    r'\bsystemctl\s+(stop|disable|mask)\s+',
    r'\btruncate\s+',
    r':\(\)\s*\{',  # fork bomb (:() { )
    r'\beval\s+.*\$\(.*\)',  # eval injection
    r'\bchown\s+-R\s+.*\s+/$',  # chown -R на /
    r'\bchown\s+.*\s+/$',  # chown на /
    r'\bfdisk\s+/dev/',
    r'\bparted\s+/dev/',
    r'\bsudo\s+rm\s+',
    r'\bdrop\s+(table|database)\b',  # SQL drop
]


def classify_tool(name: str) -> dict:
    """Возвращает классификацию инструмента."""
    # Сначала точное совпадение
    if name in TOOL_POLICY:
        return TOOL_POLICY[name]
    # Поиск по префиксу (например skill_manage_create и т.д.)
    for key, val in TOOL_POLICY.items():
        if name.startswith(key):
            return val
    # Неизвестный — консервативно WRITE
    return {
        'level': 'WRITE',
        'category': 'unknown',
        'description': f'Unknown tool: {name}',
        'requires_approval': True
    }


def is_destructive_shell(cmd: str) -> bool:
    """Проверяет, является ли shell-команда деструктивной."""
    import re
    for pat in DESTRUCTIVE_SHELL_PATTERNS:
        if re.search(pat, cmd):
            return True
    return False


def requires_approval(name: str, args: dict = None) -> bool:
    """Проверяет, требует ли вызов одобрения пользователя."""
    info = classify_tool(name)
    if info.get('requires_approval', False):
        return True
    # Спецслучай: shell с деструктивным паттерном
    if name == 'terminal' and args:
        cmd = args.get('command', '') if isinstance(args, dict) else ''
        if is_destructive_shell(cmd):
            return True
    return False


def explain(name: str) -> str:
    """Человеческое объяснение уровня риска."""
    info = classify_tool(name)
    level = info['level']
    desc = info.get('description', '')
    icon = {'READ': '👁', 'WRITE': '✏️', 'DESTRUCTIVE': '⚠️'}.get(level, '?')
    approval = ' (требует одобрения)' if info.get('requires_approval') else ''
    return f"{icon} {level}{approval} — {desc}"


# === CLI ===

def cmd_classify(name):
    print(f"Tool: {name}")
    info = classify_tool(name)
    for k, v in info.items():
        print(f"  {k}: {v}")
    print(f"\n{explain(name)}")
    if requires_approval(name):
        print("\n⛔ ТРЕБУЕТ ОДОБРЕНИЯ ПОЛЬЗОВАТЕЛЯ")
    else:
        print("\n✅ Можно вызывать без подтверждения")


def cmd_list(level=None):
    print(f"{'TOOL':40} {'LEVEL':12} {'CATEGORY':12} DESCRIPTION")
    print('-' * 100)
    for name, info in sorted(TOOL_POLICY.items()):
        if level and info['level'] != level:
            continue
        approval = '⛔' if info.get('requires_approval') else '  '
        print(f"{name:40} {info['level']:12} {info.get('category', '?'):12} {approval} {info.get('description', '')[:50]}")


def cmd_check_shell(cmd):
    print(f"Command: {cmd}")
    if is_destructive_shell(cmd):
        print("⛔ DESTRUCTIVE PATTERN DETECTED — requires approval")
    else:
        print("✅ Looks safe (no destructive patterns)")


def main():
    import argparse
    p = argparse.ArgumentParser(description='Tool policy classifier')
    sp = p.add_subparsers(dest='cmd')

    p_classify = sp.add_parser('classify', help='Classify a tool')
    p_classify.add_argument('name')

    p_list = sp.add_parser('list', help='List tools')
    p_list.add_argument('--level', choices=['READ', 'WRITE', 'DESTRUCTIVE'])

    p_check = sp.add_parser('check-shell', help='Check if shell command is destructive')
    p_check.add_argument('command', nargs='+')

    args = p.parse_args()

    if args.cmd == 'classify':
        cmd_classify(args.name)
    elif args.cmd == 'list':
        cmd_list(args.level)
    elif args.cmd == 'check-shell':
        cmd_check_shell(' '.join(args.command))
    else:
        p.print_help()


if __name__ == '__main__':
    main()
