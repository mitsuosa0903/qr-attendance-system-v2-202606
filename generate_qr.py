import qrcode
import os

def generate_qr(user_id, output_dir="qrcodes"):
    # 保存先ディレクトリを作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # QRコードのデータを定義（ここではユーザーIDを含める）
    # ※ 実際のシステム運用時は、JSON形式の文字列や暗号化されたIDなどを持たせることもあります
    data = f"{user_id}"
    
    # QRコードの生成
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # 画像として保存
    img = qr.make_image(fill_color="black", back_color="white")
    
    file_path = os.path.join(output_dir, f"user_{user_id}.png")
    img.save(file_path)
    print(f"QRコードを作成し、保存しました: {file_path}")

if __name__ == "__main__":
    # 例として、ユーザーID「EMP001」のQRコードを作成
    sample_user_id = input("発行したいユーザーID（社員番号など）を入力してください: ")
    if not sample_user_id:
        sample_user_id = "EMP001"
        
    generate_qr(sample_user_id)
