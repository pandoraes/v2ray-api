# 不再维护
使用docker-compose的大家，把docker-compose.yml里面api_alpine替换成go就好了
# 划重点
1. 用户务必保证，他的邮箱是正确邮箱格式(否则无法加入v2后端，host 务必填写没有被墙的地址）
2. 感谢NimaQu的[ss repo](https://github.com/NimaQu/shadowsocks)， 目前基本架构在他的基础上改了一个v2的中间件版本出来。（应该speedtest不会造成节点面板下线了）
3. 目前测速默认开启，6小时一次，可以选择设置成0，把它关掉
## 目前支持 docker-compose 直接安装，推荐使用版本一

## 感谢
[ThunderingII](https://github.com/ThunderingII/v2ray_python_client) 和 [spencer404](https://github.com/spencer404/v2ray_api) 关于 python 调用 api 的项目和示例。

## 项目状态

支持 [ss-panel-v3-mod_Uim](https://github.com/NimaQu/ss-panel-v3-mod_Uim) 的 webapi。 目前自己也尝试维护了一个版本, [panel](https://github.com/rico93/ss-panel-v3-mod_Uim)

目前只适配了流量记录、服务器是否在线、在线人数、负载、Speedtest 后端测速、延迟、后端根据前端的设定自动调用 API 增加用户。

v2ray 后端 kcp、tcp、ws 都是多用户共用一个端口。

也可作为 ss 后端一个用户一个端口。

## 已知 Bug

## 作为 ss 后端

面板配置是节点类型为 Shadowsocks，普通端口。

加密方式只支持：

- [x] aes-256-cfb
- [x] aes-128-cfb
- [x] chacha20
- [x] chacha20-ietf
- [x] aes-256-gcm
- [x] aes-128-gcm
- [x] chacha20-poly1305 或称 chacha20-ietf-poly1305

## 作为 V2ray 后端

这里面板设置是节点类型v2ray, 普通端口。

支持 kcp、ws、tls 由镜像 Caddy 提供。

[面板设置说明 主要是这个](https://github.com/NimaQu/ss-panel-v3-mod_Uim/wiki/v2ray-%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B)

~~~
没有CDN的域名或者ip;端口（外部链接的);AlterId;协议层;;额外参数(path=/v2ray|host=xxxx.win|inside_port=10550这个端口内部监听))

// ws 示例
xxxxx.com;443;16;ws;;path=/v2ray|host=oxxxx.com|inside_port=10550

// ws + tls (Caddy 提供)
xxxxx.com;443;16;tls;ws;path=/v2ray|host=oxxxx.com|inside_port=10550
~~~

目前的逻辑是

- 如果为外部链接的端口是 443，则默认监听本地127.0.0.1:inside_port，对外暴露443 (如果想用kcp，走443端口，建议设置流量转发)
- 如果外部端口设定不是 443，则监听 0.0.0.0:外部设定端口，此端口为所有用户的单端口，此时 inside_port 弃用。
- 默认使用 Caddy 镜像来提供 tls，控制代码不会生成 tls 相关的配置。

kcp 支持所有 v2ray 的 type：

- none: 默认值，不进行伪装，发送的数据是没有特征的数据包。

~~~
xxxxx.com;xxx换成除了443之外的端口;16;kcp;noop;
~~~

- srtp: 伪装成 SRTP 数据包，会被识别为视频通话数据（如 FaceTime）。

~~~
xxxxx.com;xxx换成除了443之外的端口;16;kcp;srtp;
~~~

- utp: 伪装成 uTP 数据包，会被识别为 BT 下载数据。

~~~
xxxxx.com;xxx换成除了443之外的端口;16;kcp;utp;
~~~

- wechat-video: 伪装成微信视频通话的数据包。

~~~
xxxxx.com;xxx换成除了443之外的端口;16;kcp;wechat-video;
~~~

- dtls: 伪装成 DTLS 1.2 数据包。

~~~
xxxxx.com;xxx换成除了443之外的端口;16;kcp;dtls;
~~~

- wireguard: 伪装成 WireGuard 数据包(并不是真正的 WireGuard 协议) 。

~~~
xxxxx.com;xxx换成除了443之外的端口;16;kcp;wireguard;
~~~

## TODO

- [x] 增加测速和负载
- [x] 全后端转向 v2ray，使用 v2ray 提供 ss 和 vmess 代理，用 v2ray 自带 api 统计流量 (Jrohy 的 [multi-v2ray](https://github.com/Jrohy/multi-v2ray) 的 templ 和部分代码思路)
- [x] 使用 docker

### [可选] 安装 BBR

看 [Rat的](https://www.moerats.com/archives/387/)
OpenVZ 看这里 [南琴浪](https://github.com/tcp-nanqinlang/wiki/wiki/lkl-haproxy)

~~~
wget -N --no-check-certificate "https://raw.githubusercontent.com/chiakge/Linux-NetSpeed/master/tcp.sh" && chmod +x tcp.sh && ./tcp.sh
~~~

Ubuntu 18.04 魔改 BBR 暂时有点问题，可使用以下命令安装：

~~~
wget -N --no-check-certificate "https://raw.githubusercontent.com/chiakge/Linux-NetSpeed/master/tcp.sh"
apt install make gcc -y
sed -i 's#/usr/bin/gcc-4.9#/usr/bin/gcc#g' '/root/tcp.sh'
chmod +x tcp.sh && ./tcp.sh
~~~

### [推荐] 脚本部署

**脚本说明：**

谷歌云 CentOS、Debian、Ubuntu 适配正常通过。

务必将脚本和生成的 Caddyfile，docker-compose.yml 文件放在同一目录下，并在该目录下运行脚本。

- [x] 脚本适配后端，安装 docker，docker-compose 并启动服务
- [x] 查看日志
- [x] 更新 config
- [x] 更新 images

~~~
mkdir v2ray-agent  &&  cd v2ray-agent
curl https://raw.githubusercontent.com/rico93/shadowsocks-munager/v2ray_api/install.sh -o install.sh && chmod +x install.sh && bash install.sh
~~~

### Docker + docker-compose 部署

**安装 Docker：**
~~~
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
~~~

**安装 docker-compose：**

[推荐] 二进制安装 ：
~~~
sudo curl -L https://github.com/docker/compose/releases/download/1.17.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
~~~

pip 安装 docker-compose
~~~
pip install -U docker-compose
~~~

bash 补全命令
~~~
curl -L https://raw.githubusercontent.com/docker/compose/1.8.0/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose
~~~

**卸载 docker-compose：**

如果是二进制包方式安装的，删除二进制文件即可。
~~~
sudo rm /usr/local/bin/docker-compose
~~~

如果是通过 pip 安装的，则执行如下命令即可删除。
~~~
sudo pip uninstall docker-compose
~~~

#### [版本一] v2ray + Caddy 提供 tls (ws)

创建 Caddyfile

~~~
{$V2RAY_DOMAIN}
{
  root /srv/www
  log ./caddy.log
  proxy {$V2RAY_PATH} localhost:10550 {
    websocket
    header_upstream -Origin
  }
  gzip
  tls {$V2RAY_EMAIL} {
    protocols tls1.0 tls1.2
    # remove comment if u want to use cloudflare ddns
    # dns cloudflare
  }
}
~~~

创建 docker-compose.yml 并修改对应项

~~~
version: '2'

services:
 v2ray:
    image: rico93/v2ray_v3:api_alpine
    restart: always
    network_mode: "host"
    environment:
      sspanel_url: "https://xxxx"
      key: "xxxx"
      docker: "true"
      speedtest: 6
      node_id: 10
    logging:
      options:
        max-size: "10m"
        max-file: "3"

 caddy:
    image: rico93/v2ray_v3:caddy
    restart: always
    environment:
      - ACME_AGREE=true
#      if u want to use cloudflare ddns service
#      - CLOUDFLARE_EMAIL=xxxxxx@out.look.com
#      - CLOUDFLARE_API_KEY=xxxxxxx
      - V2RAY_DOMAIN=xxxx.com
      - V2RAY_PATH=/v2ray
      - V2RAY_EMAIL=xxxx@outlook.com
    network_mode: "host"
    volumes:
      - ./.caddy:/root/.caddy
      - ./Caddyfile:/etc/Caddyfile
~~~

**运行：**

~~~
docker-compose up (加上 -d 后台运行）
~~~

#### [版本二] 单纯一个 v2ray

创建 docker-compose.yml 并修改对应项

~~~
version: '2'

services:
 v2ray:
    image: rico93/v2ray_v3:api_alpine
    restart: always
    network_mode: "host"
    environment:
      sspanel_url: "https://xxxx"
      key: "xxxx"
      docker: "true"
      speedtest: 6
      node_id: 10
    logging:
      options:
        max-size: "10m"
        max-file: "3"
~~~

**运行：**

~~~
docker-compose up (加上 -d 后台运行）
~~~

### Docker 部署

Pull the image（目前 Ubuntu 约 500M、alpine 约 200M）

请先根据上方方法安装 Docker，然后继续。

~~~
docker pull rico93/v2ray_v3:api_alpine

// or 

docker pull rico93/v2ray_v3:api_ubuntu

// 执行

docker run -d --network=host --name v2ray_v3_api -e node_id=1 -e key=ixidnf -e sspanel_url=https://xx -e docker=true --log-opt max-size=50m --log-opt max-file=3 --restart=always rico93/v2ray_v3:api_alpine
~~~


### 普通安装

**安装 v2ray：**

~~~
curl -L -o /tmp/go.sh https://raw.githubusercontent.com/rico93/v2ray-core/4.12.0_ips/release/install-release.sh && bash /tmp/go.sh -f --version 4.12.0
~~~

**安装依赖：**

Ubuntu：

~~~
apt-get install -y gcc python3-dev python3-pip python3-setuptools git
~~~

CentOS：

~~~
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum update
yum install -y git python36u python36u-libs python36u-devel python36u-pip gcc
python3.6 -V
~~~

**安装项目：**

~~~
git clone -b v2ray_api https://github.com/pandoraes/v2ray-api.git
cd shadowsocks-munager
cp config/config_example.yml config/config.yml
cp config/config.json /etc/v2ray/config.json
pip3 install -r requirements.txt or pip3.6 install -r requirements.txt
~~~

**修改配置：**

修改 config.yml，将 docker 设为 false 并配置 sspanel_url、key、node_id 等。
修改 /etc/v2ray/config.json 如果你修改了 config.yml里的 api_port, 修改config.json的12行。
**运行：**

~~~
screen -S v2ray
python3 run.py --config-file=config/config.yml or python3.6 run.py --config-file=config/config.yml
~~~
##相关错误
错误提示：RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment.  Consult http://click.pocoo.org/python3/for mitigation steps.
方法：export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8   &&python3.6 run.py --config-file=config/config.yml
## 相似的项目

[SSRPanel](https://github.com/ssrpanel/SSRPanel)，目前自带了一个 v2ray 的后端支持。

[ss-panel-v3-mod_Uim](https://github.com/NimaQu/ss-panel-v3-mod_Uim) WIKI 中有提及一个收费版的 v2ray 适配。


