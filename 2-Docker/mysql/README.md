# MySQL Docker 部署

用 Docker Compose 跑一个 MySQL 8.0，数据挂载到本地，适合开发测试用。

---



## 文件结构

.
├── docker-compose.yml   # 启动配置
├── data/                # 数据文件（自动生成）
├── logs/                # 日志（自动生成）
├── conf/                # 配置文件（放 my.cnf）
└── README.md



## 快速开始

### 1. 配置镜像加速（推荐）

为了拉取镜像更快，推荐配置阿里云镜像加速器。

**获取加速器地址：**
登录阿里云 → 容器镜像服务 → 镜像加速器，获取专属地址（格式：`https://xxx.mirror.aliyuncs.com`）

**配置 Docker：**

- Windows：Docker Desktop → Settings → Docker Engine
- Linux/macOS：编辑 `/etc/docker/daemon.json`

```json
{
  "registry-mirrors": ["https://xxx.mirror.aliyuncs.com"]
}
```



保存后重启 Docker。

配置成功后，直接用 `mysql:8.0` 即可享受加速。

### 2. 编写 docker-compose.yml

```yaml
services:
  mysql:
    # MySQL 8.0 官方镜像（配合镜像加速器使用）
    image: mysql:8.0
    # 容器名称
    container_name: mysql-db
    # 容器退出后自动重启（除非手动停止）
    restart: unless-stopped
    ports:
      # 宿主机端口:容器端口
      - "3306:3306"
    environment:
      # root 用户密码（必填）
      MYSQL_ROOT_PASSWORD: Root_2026_Secure!
      # 容器启动时自动创建的数据库
      MYSQL_DATABASE: appdb
      # 容器时区（北京时间）
      TZ: Asia/Shanghai
    volumes:
      # 数据持久化：宿主机 ./data 映射到容器数据目录
      - ./data:/var/lib/mysql
      # 日志持久化：宿主机 ./logs 映射到容器日志目录
      - ./logs:/var/log/mysql
      # 配置文件挂载：宿主机 ./conf 下的 my.cnf 会被自动加载
      - ./conf:/etc/mysql/conf.d
    # 容器启动时追加的 MySQL 参数
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --default-authentication-plugin=mysql_native_password
    deploy:
      resources:
        limits:
          # CPU 限制
          cpus: '2'
          # 内存限制
          memory: 2G
```



### 3. 启动并验证

```bash
# 启动
docker compose up -d

# 查看日志（看到 ready for connections 就说明好了）
docker logs -f mysql-db

# 登录测试
docker exec -it mysql-db mysql -uroot -pRoot_2026_Secure!
```

---



## 连接信息

| 项目     | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 主机     | localhost                                                    |
| 端口     | 3306                                                         |
| 数据库   | appdb                                                        |
| 用户名   | root                                                         |
| 密码     | Root_2026_Secure!                                            |
| JDBC URL | `jdbc:mysql://localhost:3306/appdb?useSSL=false&serverTimezone=Asia/Shanghai` |

---



## 环境变量说明

| 变量                  | 说明                         |
| --------------------- | ---------------------------- |
| `MYSQL_ROOT_PASSWORD` | root 密码（必填）            |
| `MYSQL_DATABASE`      | 容器启动时自动创建的数据库   |
| `TZ`                  | 时区，设置为 `Asia/Shanghai` |

---



## 关于认证插件

默认配置中已添加 `--default-authentication-plugin=mysql_native_password`，使用 MySQL 5.7 兼容的密码认证方式，可以避免 `Public Key Retrieval is not allowed` 等连接问题。

如需修改 root 用户认证方式（数据已存在的情况），进入容器执行：

```sql
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Root_2026_Secure!';
FLUSH PRIVILEGES;
```

---



## 自定义配置（可选）

在 `./conf` 目录下新建 `my.cnf` 文件，容器启动时会自动加载：

```ini
[mysqld]
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
max_connections=200
innodb_buffer_pool_size=512M

[client]
default-character-set=utf8mb4
```

---



## 日常操作

```bash
# 看日志
docker logs -f mysql-db

# 进容器
docker exec -it mysql-db bash

# 登录 MySQL
docker exec -it mysql-db mysql -uroot -pRoot_2026_Secure!

# 启停容器
docker compose start
docker compose stop

# 重启容器
docker compose restart

# 删容器（数据保留）
docker compose down

# 删容器 + 删数据（慎用）
docker compose down -v
Remove-Item -Recurse -Force ./data, ./logs
```

---



## 数据存在哪

| 目录   | 内容                           |
| ------ | ------------------------------ |
| ./data | 核心数据文件（删容器不丢数据） |
| ./logs | 错误日志、慢查询日志           |
| ./conf | 自定义配置文件                 |

---



## 常见问题

### 端口被占用

修改端口映射：`"3307:3306"`



### 容器起不来，日志显示权限错误

删掉 `./data` 目录，让 MySQL 重新初始化：

```powershell
docker compose down
Remove-Item -Recurse -Force ./data
docker compose up -d
```



### 连接报错：Public Key Retrieval is not allowed

已在 `command` 中配置 `--default-authentication-plugin=mysql_native_password`，新建容器不会有此问题。

如果数据已存在且报错，进入容器执行：

```sql
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Root_2026_Secure!';
FLUSH PRIVILEGES;
```



### 字符集乱码

MySQL 8.0 默认 utf8mb4，一般不会有问题。如遇问题检查 `my.cnf` 中的字符集配置。

---



## 版本

- MySQL：8.0
- 镜像：`mysql:8.0`（官方镜像，配合镜像加速器使用）

---



## 声明

只用于开发测试，生产环境请谨慎评估。