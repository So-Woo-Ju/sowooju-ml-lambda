# sowooju-ml-lambda

## Getting Started

### 1. Docker 클라이언트 인증
```
$ aws configure
$ aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <sowooju lambda ECR 주소>
```

### 2. 도커 이미지를 빌드
```
docker build -t sowooju-lamda-tensorflow .
```

### 3. 이미지에 태그를 지정하여 이 리포지토리에 푸시
```
docker tag <sowooju lambda ECR 이름>:latest <sowooju lambda 이미지 URI>
```

### 4. 이 이미지를 새로 생성한 AWS 리포지토리로 푸시
```
docker push <sowooju lambda 이미지 URI>
```

### 5. lambda 함수 내에서 `새이미지 배포`를 클릭

### 6. S3에 업로드하면 트리거 되어서, 반환값 저장