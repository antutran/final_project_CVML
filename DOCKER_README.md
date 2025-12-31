# AI Fashion Studio - Docker Deployment

## Chạy ứng dụng với Docker

### Yêu cầu
- Docker Desktop phải được cài đặt và đang chạy

### Các bước thực hiện

#### 1. Khởi động Docker Desktop
Mở ứng dụng Docker Desktop trên máy tính của bạn và đợi nó khởi động hoàn toàn.

#### 2. Build Docker Images
```bash
cd /Users/tuantran/Downloads/CVML
docker-compose build
```

Quá trình build sẽ mất vài phút lần đầu tiên.

#### 3. Khởi chạy ứng dụng
```bash
docker-compose up
```

Hoặc chạy ở chế độ nền (background):
```bash
docker-compose up -d
```

#### 4. Truy cập ứng dụng

Từ **máy chủ** (máy đang chạy Docker):
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

Từ **các thiết bị khác trong mạng**:
- Frontend: http://<ĐỊA_CHỈ_IP_MÁY_CHỦ>:3000
- Backend API: http://<ĐỊA_CHỈ_IP_MÁY_CHỦ>:8000

Để tìm địa chỉ IP của máy chủ:
- **macOS**: Mở System Settings > Network, xem IP address
- Hoặc chạy lệnh: `ifconfig | grep "inet " | grep -v 127.0.0.1`

### Tắt ứng dụng

```bash
docker-compose down
```

Để xóa hết dữ liệu và volume:
```bash
docker-compose down -v
```

### Xem logs

```bash
# Xem logs của tất cả services
docker-compose logs

# Xem logs của frontend
docker-compose logs frontend

# Xem logs của backend
docker-compose logs backend

# Theo dõi logs real-time
docker-compose logs -f
```

### Rebuild sau khi thay đổi code

```bash
docker-compose down
docker-compose build
docker-compose up
```

## Lưu ý quan trọng

1. **Firewall**: Nếu không thể truy cập từ các thiết bị khác, kiểm tra firewall của máy chủ và cho phép kết nối đến port 3000 và 8000.

2. **Cùng mạng**: Các thiết bị phải cùng mạng wifi/LAN với máy chủ.

3. **Dữ liệu**: Dữ liệu session và outfits sẽ được lưu trong Docker volumes và được giữ lại khi restart container.

4. **Performance**: Lần chạy đầu tiên sẽ lâu hơn do phải download base images và build ứng dụng.
