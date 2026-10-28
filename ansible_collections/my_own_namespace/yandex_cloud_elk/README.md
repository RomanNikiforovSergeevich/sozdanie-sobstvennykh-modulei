# my_own_namespace.yandex_cloud_elk

Коллекция для управления Observability-стеком (ClickHouse, Vector, Lighthouse) в Yandex Cloud.

## Модули

### `my_own_module`

Создаёт текстовый файл на удалённом хосте.

**Параметры:**
- `path` (обязательный) — путь к файлу.
- `content` (обязательный) — содержимое файла.

**Пример:**
```yaml
- name: Create file
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: /tmp/test.txt
    content: "Hello"

Роли
my_own_role

Обёртка над модулем my_own_module.

Переменные:

    my_own_role_path — путь к файлу (по умолчанию /tmp/default_file.txt).

    my_own_role_content — содержимое (по умолчанию Default content from role).

Сборка и установка:

ansible-galaxy collection build
ansible-galaxy collection install my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz
