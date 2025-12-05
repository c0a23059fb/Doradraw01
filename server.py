import http.server
import os
import sys


PORT = 8888

# CGIハンドラの設定
# これにより、cgi-bin または cgi_data フォルダ内のスクリプトが実行可能になります
class CustomCGIHandler(http.server.CGIHTTPRequestHandler):
    cgi_directories = ['/cgi-bin', '/cgi_data']

def run():
    # エラー回避のため、socketserver.TCPServer ではなく http.server.HTTPServer を使用
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, CustomCGIHandler)
    
    print(f"Starting server at http://localhost:{PORT}")
    print("Allowed CGI directories: /cgi-bin, /cgi_data")
    print("To stop the server, press Ctrl+C")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)

if __name__ == '__main__':
    # フォルダ存在確認（親切機能）
    if not os.path.exists('cgi-bin') and not os.path.exists('cgi_data'):
        print("【注意】 'cgi-bin' または 'cgi_data' フォルダが見つかりません。")
        print("pythonスクリプト(save_data.py)を入れたフォルダを作成してください。")
    
    run()