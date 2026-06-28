FROM nginx:alpine

# 1. 将前端静态文件复制到 Nginx 的默认托管目录
COPY index.html /usr/share/nginx/html/index.html

# 2. 修改 Nginx 配置，将默认的 80 端口改为 Cloud Run 期望的 8080 端口
RUN sed -i 's/listen       80;/listen       8080;/g' /etc/nginx/conf.d/default.conf

# 3. 暴露 8080 端口
EXPOSE 8080

# 4. 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
