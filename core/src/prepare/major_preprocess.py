import re
from bs4 import BeautifulSoup

class MajorInfo:
  '''
    MajorData describes a major blog.
    @param major major's name
    @param desc major's description
    @param additional some additional data
  '''
  def __init__(self, major: str, desc: str, additional:str):
    self.major_name = major
    self.description = desc
    self.additional = additional

'''
This class preprocess major blogs
'''
class MajorPreprocess:

  def __init__(self):
    self.name = "major preprocessor"
    self.description = "this class preprocess major blogs"


  '''
    This method run full clean for a major blog.
    @param html_path the path to the html file
    @return a fully clean major blog ready to be use
  '''
  def clean(self, html_path: str) -> str:
    html = self.clean_format(html_path=html_path)
    data = self.clean_data(page_content=html)

    pass

  '''
    This method cleans format in a major blog.
    example: https://admission.tdtu.edu.vn/dai-hoc/nganh-hoc/khoa-hoc-may-tinh
    @param html_path is the path to the html file
    @return the clean content of the html file
  '''
  def clean_format(self, html_path: str) -> str:
    with open(html_path) as f:
      content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    removes = [".header-main"]
    [soup.select_one(rem).decompose() for rem in removes]
    doc = soup.get_text()
    strips = ["\n{3,}", "\s{3,}", "\t{3, }"]
    replaces = ["\n", " ", " "]
    for strip, replace in zip(strips, replaces):
      doc = re.sub(strip, replace, doc)
    return doc
  
  '''
  This method cleans unecessary data in a major blog.
  @param page_content is the content of a major blog
  @return a new page
  '''
  def clean_data(self, page_content: str) -> str:
    page_content = re.sub(r'\n.+?\|', '', page_content)
    page_content = page_content.replace("Tuyển sinh Nhảy đến nội dung x\n", "")
    page_content = page_content.replace("\nĐăng ký xét tuyển Đặt câu hỏi ", "")
    page_content = re.sub(r'Phương thức tuyển sinh.*?Gọi hotline tư vấn', '', page_content, flags=re.DOTALL)
    page_content = re.sub(r'Vì sao nên chọn ngành.*?Các chương trình của ngành', 'Các chương trình của ngành', page_content, flags=re.DOTALL)
    page_content = re.sub(r'Cựu sinh viên nói gì.*$', '', page_content, flags=re.DOTALL)
    page_content = re.sub(r'Xem thông tin chi tiết về (chương trình đào tạo Chuẩn đầu ra|chuẩn đầu ra Phương thức xét tuyển riêng)', '', page_content)
    page_content = re.sub(r'\n+', '\n', page_content)
    page_content = re.sub(r'\nTìm hiểu về [^\n]+\nWebsite [^\n]+\nKhám phá [^\n]+\n', '\n', page_content)
    return page_content

  '''
  This method extracts major's title in a major blog.
  @param page_content is the content of a major blog
  @return a title
  '''
  def extract_major_title(self, page_content: str) -> str:
    opening_match = re.search(r'\n(.+?) \|', page_content)
    major_keyword = opening_match.group(1) if opening_match else None
    return major_keyword
  

  '''
  This method extracts major's information in a major blog.
      @param page_content is the content of a major blog.
      @param major_keyword is the major's title (e.g. keyword)
      @return a MajorData object
  '''
  def extract_major_info(self, page_content: str, major_keyword: str) -> MajorInfo:
    # Remove unnecessary content
    page_content = self.clean_data(page_content)
    # Extract major title
    major_match = re.search(major_keyword, page_content)
    major = major_match.group(0) if major_match else None
    # Extract description
    description_match = re.search(f'{major_keyword}(.+?)Thông tin cần biết', page_content, re.DOTALL)
    description = description_match.group(1).strip() if description_match else None
    if major and description and major_keyword in description[len(major_keyword):]:
      description = description.replace(major, '', 1).strip()
    # Extract aditional description
    additional_description_match = re.search(r'Thông tin cần biết(.+?)$', page_content, re.DOTALL)
    additional_description = additional_description_match.group(1).replace('Thông tin cần biết ', '').strip() if additional_description_match else None
    additional_description = re.sub(r'năm Chương trình đào tạo', 'năm', additional_description)
    additional_description = re.sub(r'tại Trường liên kết\) Chương trình đào tạo', 'tại Trường liên kết)', additional_description)
    return MajorInfo(major, description, additional_description)