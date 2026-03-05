# 技术栈识别规则

## 前端识别

| 特征 | 技术 |
|------|------|
| `package.json` + `src/App.jsx` | React |
| `package.json` + `src/main.js` + Vite | Vue 3 |
| `package.json` + `src/App.vue` | Vue 2/3 |
| `angular.json` | Angular |
| `next.config.js` | Next.js |
| `nuxt.config.js` | Nuxt |
| `svelte.config.js` | Svelte |

## 后端识别

| 特征 | 技术 |
|------|------|
| `pom.xml` + `src/main/java` | Java + Maven |
| `build.gradle` + `src/main/java` | Java + Gradle |
| `requirements.txt` + `app.py` | Python/Flask |
| `requirements.txt` + `manage.py` | Python/Django |
| `go.mod` + `main.go` | Go |
| `package.json` + `server/` | Node.js/Express |
| `Cargo.toml` | Rust |

## 数据库识别

| 特征 | 数据库 |
|------|--------|
| `prisma/schema.prisma` | Prisma ORM |
| `sequelize` | Sequelize ORM |
| `typeorm` | TypeORM |
| `SQLAlchemy` | Python SQLAlchemy |
| `mybatis` | MyBatis |
| `.sql` 文件 | 直接 SQL |
| `mongodb` 连接 | MongoDB |
