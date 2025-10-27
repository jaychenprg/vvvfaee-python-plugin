import hashlib
import json
import os


#  补充错误没有处理 JSON 解析错误
#  补充错误没有处理文件读写错误
#  补充错误没有处理文件不存在
#  补充错误没有对 cache_file_name 参数进行验证
def get_cached(text, cache_file_name):
    try:
        # 获取缓存文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(current_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file_path = os.path.join(cache_dir, cache_file_name)
        
        # 计算哈希值
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # 读取缓存
        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as cache_file:
                    cache_data = json.load(cache_file)
                    return cache_data.get(text_hash)
            except json.JSONDecodeError:
                return None
        return ""
    except Exception:
        return ""


# 需要添加错误处理
def write_cached(text, content, cache_file_name):
    # 验证输入参数
    if not isinstance(text, str) or not isinstance(cache_file_name, str):
        raise ValueError("text 和 cache_file_name 必须是字符串类型")
    if not cache_file_name:
        raise ValueError("cache_file_name 不能为空")
        
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(current_dir, 'cache')
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 修正了路径构建的冗余
        cache_file_path = os.path.join(cache_dir, cache_file_name)
        
        # 计算文本的哈希值
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # 初始化缓存数据
        cache_data = {}
        
        # 如果缓存文件存在，读取现有数据
        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as cache_file:
                    cache_data = json.load(cache_file)
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用空字典继续
                cache_data = {}
            except IOError as e:
                raise IOError(f"读取缓存文件失败: {str(e)}")
        
        # 更新缓存数据
        cache_data[text_hash] = content
        
        # 将更新后的数据写入缓存文件
        try:
            with open(cache_file_path, 'w', encoding='utf-8') as cache_file:
                json.dump(cache_data, cache_file, ensure_ascii=False, indent=4)
        except IOError as e:
            raise IOError(f"写入缓存文件失败: {str(e)}")
            
    except Exception as e:
        raise Exception(f"缓存写入过程发生错误: {str(e)}")
