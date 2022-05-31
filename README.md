# sowooju-ml-lambda

## 프로젝트 개요

저희 서비스는 폐쇄형 자막을 제공해주는 배리어프리 자막 서비스입니다. **폐쇄형자막**은 웃음소리, 천둥소리 등 비언어 소리를 자막으로 표시합니다. 이런 폐쇄형 자막이 장애인들에게 필요하지만, 시간과 자원이 많이 필요해 제공하지 않는 경우가 대부분입니다. 

폐쇄형 자막은 장애인 뿐만 아니라 비장애인들도 선호하는데요. 놓치는 것 없이 볼 수 있고 외출 시 이어폰을 들고 나오지 않았을 경우 등 상황에 제약받지 않고 컨텐츠를 즐길 수 있는 장점이 있기 때문입니다. 현재는 폐쇄형 자막 중 비언어적 소리 역시 사람이 입력하여 시간이 오래 걸리는 문제점이 있기 때문에 저희 서비스는 AI를 이용한 자동화로 빠르게 폐쇄형자막을 제공하고자 합니다.



## 프로젝트 아키텍쳐

![image](https://user-images.githubusercontent.com/66551410/171229067-4a5bbd76-e863-4fd2-bb2a-b37e5de55801.png)



## 프로젝트 기술 스택

|                         Backend (AI)                         |
| :----------------------------------------------------------: | 
| ![AWS Lambda](https://img.shields.io/badge/Lambda-white?style=flat-square&logo=amazon-aws&color=FF9900) ![AWS Lambda](https://img.shields.io/badge/TensorFlow-white?style=flat-square&logo=tensorflow&color=FF6F00&logoColor=white) |


# Backend (AI)

## 사용한 기술

- MFCC
- YAMNet
- AWS Lambda

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


## Package

```bash
추가해야합니다.
```



## Contributors

|                 주효정                 |                  김소미                  |                    박소현                    |               Sunwoo Ho                |
| :------------------------------------: | :--------------------------------------: | :------------------------------------------: | :------------------------------------: |
| [@jhj2713](https://github.com/jhj2713) | [@somii009](https://github.com/somii009) | [@Sohyun-Dev](https://github.com/Sohyun-Dev) | [@hocaron](https://github.com/hocaron) |
|               React, AI                |               Backend, AI                |                 Backend, AI                  |              Backend, AI               |
