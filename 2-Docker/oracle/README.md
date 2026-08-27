# Oracle 19c Docker 部署

用 Docker Compose 跑一个 Oracle 19c，数据挂载到本地，适合开发测试用。

---

## 文件结构

.
├── docker-compose.yml   # 启动配置
├── oradata/             # 数据文件（自动生成）
├── logs/                # 日志（自动生成）
├── backup/              # 备份目录（自动生成）
└── README.md



---

## 启动步骤

### 1. 编写 docker-compose.yml

```yaml
services:
  oracle-free:
    image: registry.cn-hangzhou.aliyuncs.com/zhuyijun/oracle:19c
    container_name: oracle-free-db
    restart: unless-stopped
    ports:
      - "1521:1521"
      - "5500:5500"
    environment:
      ORACLE_PWD: Ora_2026_Secure!
      ORACLE_SID: ORCL
      ORACLE_PDB: ORCLPDB
      ORACLE_CHARACTERSET: AL32UTF8
    volumes:
      - ./oradata:/opt/oracle/oradata
      - ./logs:/opt/oracle/diag/rdbms
      - ./backup:/opt/oracle/backup
    shm_size: 2g
    mem_limit: 4g
    cpus: 2
```



### 2. 启动并查看日志

```bash
docker compose up -d
docker logs -f oracle-free-db
```

看到 `DATABASE IS READY TO USE!` 就说明好了，大概等 3~5 分钟。



### 3. 连上去试试

```bash
# 推荐：操作系统认证，不用输密码
docker exec -it oracle-free-db sqlplus / as sysdba

# 或者用密码连 PDB
docker exec -it oracle-free-db sqlplus system/Ora_2026_Secure!@//localhost:1521/ORCLPDB
```

---



## 连接参数

| 项目     | 值                                           |
| -------- | -------------------------------------------- |
| 主机     | localhost                                    |
| 端口     | 1521                                         |
| 服务名   | ORCLPDB                                      |
| 用户名   | system                                       |
| 密码     | Ora_2026_Secure!                             |
| JDBC URL | `jdbc:oracle:thin:@//localhost:1521/ORCLPDB` |

图形化工具（DBeaver、Navicat、DataGrip）直接用上面这套参数填就行。

---



## Web 管理页

地址：`https://localhost:5500/em`  
账号：`system` / `Ora_2026_Secure!`  
证书警告忽略，继续访问即可。

---



## 日常操作

```bash
# 看日志
docker logs -f oracle-free-db

# 进容器
docker exec -it oracle-free-db bash

# 启停容器
docker compose start
docker compose stop

# 删容器（数据保留）
docker compose down

# 删容器 + 删数据（慎用）
docker compose down -v
rm -rf ./oradata ./logs ./backup
```

---



## 数据存在哪

| 目录      | 内容         |
| --------- | ------------ |
| ./oradata | 核心数据文件 |
| ./logs    | 告警日志     |
| ./backup  | 自己放备份用 |

删容器不会丢数据，只有删目录才会。

---



## 常见问题

**启动慢或起不来**  
可能是内存不够。把 `mem_limit` 改成 `6g` 或 `8g` 再试。

**连不上，报 ORA-12514**  
进容器查一下服务名：
```bash
docker exec -it oracle-free-db sqlplus / as sysdba
show parameter service_names;
```
出来的值就是你要填的服务名。

**5500 端口打不开**  
检查端口是否被占用，或者防火墙有没有拦。

---



## 版本

- Oracle：19c Enterprise Edition
- 镜像：`registry.cn-hangzhou.aliyuncs.com/zhuyijun/oracle:19c`

---



## 声明

只用于开发测试，生产环境请买 Oracle 正版授权。