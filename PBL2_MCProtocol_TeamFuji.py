#!/usr/bin/env python
# coding: utf-8

# In[5]:


# PBL（Project Based Learning）ロングターム 〜画像解析〜
#  MCProtocol（Raspberrypi or PC と kv-7500の通信）
#
#  作成  ： TeamFuji
#  作成日： 2019/11/18


#必要なモジュールの読み込み
import socket
import time
import sys

# *********************************************************************************************
# 通信プロトコルの関数化（関数名は読み込みするデバイス№に合わせてます）


# 設備の停止コマンド-----------------------------------------------------------------------------
class StopMachine:
    # Initialize（接続するＩＰとポートの登録）
    def __init__(self, sock=None):
        
        print('StopMachine_init')
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock

# 設備の運転を停止させる
    def TxRx_MR2105(self):

        #データ書き込み要求の送信
        device='M*000337'     # デバイス名 MR2101
        print('mysend:', device)
        self.sock.sendto(('500000FF03FF000019001014010001' + device + '00011').encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信
        print('myreceive')
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] == '0000':
            print ('受信正常：',data[22:])
        else:
            print ('TxRx_MR2105エラー発生：',data[18:]) 
            sys.exit(1)

        #書き込み結果がPLC内で反映されたか確認
        ret = '0'
        while ret == '0':
            # データ要求を送信
            device='M*0000320'     # デバイス名 MR2000
            print('mysend:', device)
            self.sock.sendto(('500000FF03FF000018001004010001' + device + '0001').encode('utf-8'),
                             (host_ip,host_port))
            # 受信
            print('myreceive')
            data=[]
            data=(self.sock.recv(1024)).decode('utf-8')
            #受信状態の確認
            if data[18:22] == '0000':
                print ('受信正常：',data[22:])
                ret = data[22:]
            else:
                print ('TxRx_MR2105エラー発生：',data[18:]) 
                sys.exit(1)

        #データ書き込み要求の送信 ( 1にしたものを０に戻す)
        device='M*000337'     # デバイス名 MR2101
        print('mysend:', device)
        self.sock.sendto(('500000FF03FF000019001014010001' + device + '00010').encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信
        print('myreceive')
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] == '0000':
            print ('受信正常：',data[22:])
            ret = data[22:]
        else:
            print ('TxRx_MR2105エラー発生：',data[18:])
            sys.exit(1)
        
        return ret
            
# 設備との通信各コマンド-----------------------------------------------------------------------------          
class MySocketUDP:
    
    # Initialize（接続するＩＰとポートの登録）
    def __init__(self, sock=None):
        
        print('MySocketUDP_init')
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock

# 設備運転中かどうか確認
    def TxRx_MR2000(self):

        # データ要求を送信
        device='M*000320'     # デバイス名 MR2000
        self.sock.sendto(('500000FF03FF000018001004010001' + device + '0001').encode('utf-8'),
                         (host_ip,host_port))
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] == '0000':
            ret = data[22:]
        else:
            print ('TxRx_MR2000_エラー発生：',data[18:]) 
            StopMachine.TxRx_MR2105()
            sys.exit(1)

        return ret

# コンベアが動作しているかどうか確認
    def TxRx_MR208(self):

        # データ要求を送信
        device='M*000040'     # デバイス名 MR208
        self.sock.sendto(('500000FF03FF000018001004010001' + device + '0001').encode('utf-8'),
                         (host_ip,host_port))
        # 受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] == '0000':
            ret = data[22:]
        else:
            print ('TxRx_MR208_エラー発生：',data[18:]) 
            StopMachine.TxRx_MR2105()
            sys.exit(1)
        
        return ret

# 撮像トリガの受信
    def TxRx_MR2011(self):

        # データ要求を送信
        device='M*000331'     # デバイス名 MR2011
        self.sock.sendto(('500000FF03FF000018001004010001' + device + '0001').encode('utf-8'),
                         (host_ip,host_port))
        # 受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] == '0000':
            ret = data[22:]
        else:
            print ('TxRx_MR2011_エラー発生：',data[18:]) 
            StopMachine.TxRx_MR2105()
            sys.exit(1)

        return ret

# コンベアの再起動
    def TxRx_MR2105(self):

        #データ書き込み要求の送信
        device='M*000336'     # デバイス名 MR2100
        self.sock.sendto(('500000FF03FF000019001014010001' + device + '00011').encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] != '0000':
            print ('TxRx_MR2105_step1エラー発生：',data[18:])
            StopMachine.TxRx_MR2105()
            sys.exit(1)

        #書き込み結果がPLC内で反映されたか確認
        ret = '0'
        while ret == '0':
            # データ要求を送信
            device='M*000341'     # デバイス名 MR2105
            self.sock.sendto(('500000FF03FF000018001004010001' + device + '0001').encode('utf-8'),
                             (host_ip,host_port))
            # 受信
            data=[]
            data=(self.sock.recv(1024)).decode('utf-8')
            #受信状態の確認
            if data[18:22] == '0000':
                ret = data[22:]
            else:
                print ('TxRx_MR2105_step2エラー発生：',data[18:]) 
                StopMachine.TxRx_MR2105()
                sys.exit(1)

        #データ書き込み要求の送信 ( 1にしたものを０に戻す)
        device='M*000336'     # デバイス名 MR2100
        self.sock.sendto(('500000FF03FF000019001014010001' + device + '00010').encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] == '0000':
            ret = data[22:]
        else:
            print ('TxRx_MR2105_step3エラー発生：',data[18:]) 
            StopMachine.TxRx_MR2105()
            sys.exit(1)

        return ret

# 判定結果をＰＬＣに送る
    def TxRx_MR2107(self, msg):

        # DM30へ判定結果を書き込む
        device='D*000030'     # デバイス名 DM30
        self.sock.sendto(('500000FF03FF00001C001014010000' + device + '0001000' + msg).encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] != '0000':
            print ('TxRx_MR2107_step1エラー発生：',data[18:])
            StopMachine.TxRx_MR2105()
            sys.exit(1)
        
        # DMの値が送信データと一致しているか確認
        device='D*000030'     # デバイス名DM30
        self.sock.sendto(('500000FF03FF000018001004010000' + device + '0001').encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信                         
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
                             
        #受信状態の確認
        if data[18:22] == '0000':
            if int(data[22:], 16) != int(msg):
                DM_err = True
                print('ＤＭ値照合エラー：',data[18:])
                sys.exit(1)
        else:
            print ('TxRx_MR2107_step2エラー発生：',data[18:])
            StopMachine.TxRx_MR2105()
            sys.exit(1)
                             
        #データ書き込み要求の送信
        device='M*000338'     # デバイス名 MR2102
        self.sock.sendto(('500000FF03FF000019001014010001' + device + '00011').encode('utf-8'),
                         (host_ip,host_port))
        #結果の受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        #受信状態の確認
        if data[18:22] != '0000':
            print ('TxRx_MR2107_step3エラー発生：',data[18:])
            StopMachine.TxRx_MR2105()
            sys.exit(1)

        #書き込み結果がPLC内で反映されたか確認
        ret = '0'
        while ret == '0':
            # データ要求を送信
            device='M*000343'     # デバイス名 MR2107
            self.sock.sendto(('500000FF03FF000018001004010001' + device + '0001').encode('utf-8'),
                             (host_ip,host_port))
            # 受信
            data=[]
            data=(self.sock.recv(1024)).decode('utf-8')
            #受信状態の確認
        # 受信状態の確認
            if data[18:22] == '0000':
                ret = data[22:]
            else:
                print ('TxRx_MR2107_step4エラー発生：',data[18:]) 
                StopMachine.TxRx_MR2105()
                sys.exit(1)

        # データ書き込み要求の送信 ( 1にしたものを０に戻す)
        device='M*000338'     # デバイス名 MR2102
        self.sock.sendto(('500000FF03FF000019001014010001' + device + '00010').encode('utf-8'),
                         (host_ip,host_port))
        # 結果の受信
        data=[]
        data=(self.sock.recv(1024)).decode('utf-8')
        # 受信状態の確認
        if data[18:22] == '0000':
            ret = data[22:]
        else:
            print ('TxRx_MR2107_step5エラー発生：',data[18:])
            StopMachine.TxRx_MR2105()
            sys.exit(1)
            
        return ret


# In[6]:


# *********************************************************************************************
def main():

    # コンベアが 動いていなければ 1秒周期で確認する
    ret_MR208 = '1'
    print ('ｺﾝﾍﾞｱの停止を待っています。')
    while ret_MR208 != '0':
        time.sleep(1)
        ret_MR208 = myapp.TxRx_MR208()
    print ('ｺﾝﾍﾞｱが停止しました。')
    
    #  撮像トリガが入るのを待つ
    ret_MR2011 = '0'
    while ret_MR2011 != '1':
        ret_MR2011 = myapp.TxRx_MR2011()
    print ('撮像ｽﾀｰﾄ信号が入りました')
    
    #  撮像及び 判定処理 
    #  仮で戻り値を 良品：０ 、 欠け：１ 、 キズ：２、打痕：３、その他：４ としています
    #  次の2行は動作確認用として仮で設置 （推論モデルとドッキングしたら削除）
    ret_predict = 4
    ret_predict = str(input())
    print ('判定結果:',ret_predict)
    
    # 判定結果を PLCに送る
    myapp.TxRx_MR2107(ret_predict)
    print ('判定結果を次工程へ送りました。')
    
    # コンベアを再起動する
    print ('次のﾜｰｸを投入してください。')
    myapp.TxRx_MR2105()
    


# In[7]:


# *********************************************************************************************
if __name__ == '__main__':
    
    # 接続先イーサネットの情報
    host_ip = '192.168.3.20'     #このIPは接続するPLCに合わせ変更する
    host_port = 5000             #このポート№は PLCに合わせる（取説 or ユニットの設定値を参照）
    
    # 接続処理
    StopMachine= StopMachine()
    myapp = MySocketUDP()
    
    
    try:
        while True:  # なんらかの重い処理 (for だったり while だったり。。。)
        
            # 自動起動しているか確認（動いていなければ 1秒ごとに確認を続ける）  
            ret_MR2000 = '0'
            print ('設備と通信を開始しました。')
            while ret_MR2000 != '1':
                time.sleep(1)
                ret_MR2000 = myapp.TxRx_MR2000()
                if ret_MR2000 == '1':
                    print ('設備の自動運転が起動しました。')

            # 自動運転中の間は 判定処理を続行する
            while ret_MR2000 == '1':
                main()
                ret_MR2000 = myapp.TxRx_MR2000()

    except KeyboardInterrupt:
       
        print('Raspberrypiの動作が停止しました。')
        mystop.TxRx_MR2105()  # 設備停止
        sys.exit(0)
    # 欲を言えば  ラズパイが動いていることを PLCに知らせるようにしたいな・・・
    # 電源OFFや ケーブル断は TCP接続なら確認方法ありそうだが プログラムがRUNしていないことをどう知らせる？