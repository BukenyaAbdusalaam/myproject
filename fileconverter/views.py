from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import pandas as pd
import zipfile
from io import BytesIO

# Form to upload Excel file
class UploadFileForm(forms.Form):
    file = forms.FileField()


def format_row(row):
    free_space = ' ' * 10 
    date_field = str(int(row['Date'])) if not pd.isna(row['Date']) else '0'.ljust(18)
    code_field = str(int(row['Account Code'])) if not pd.isna(row['Account Code']) else '0'.ljust(7)
    amount_field = str(int(row['Amount'])) if not pd.isna(row['Amount']) else '0'.rjust(42)
    currency_field = str(row['Currency']) if not pd.isna(row['Currency']) else '0'.rjust(4)
    
    date_field = date_field.ljust(18)
    code_field = code_field.ljust(7)
    amount_field = amount_field.rjust(42)
    currency_field = currency_field.rjust(4)
    
    return f"{free_space}{date_field}{code_field}{amount_field} {currency_field}"


# Function to process Excel file and generate txt files
def generate_txt_files(excel_file):
    # Read the uploaded Excel file
    xls = pd.ExcelFile(excel_file)
    txt_files = {}
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name )
# skiprows=4
        # Replace NaN values with 0
        df.fillna(0, inplace=True)

        # Apply the formatting function to each row
        formatted_rows = "\n".join(df.apply(format_row, axis=1))

        # Add the formatted rows to the dictionary with the sheet name as the file name
        txt_files[f"{sheet_name}.txt"] = formatted_rows
    
    return txt_files

# View to handle file upload and download
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']

            # Generate txt files from the uploaded Excel file
            files = generate_txt_files(excel_file)
            
            # Create an in-memory zip file
            in_memory = BytesIO()
            with zipfile.ZipFile(in_memory, 'w') as zip_file:
                for filename, content in files.items():
                    zip_file.writestr(filename, content)
            
            # Prepare the HTTP response with the zip file
            in_memory.seek(0)
            response = HttpResponse(in_memory, content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename="converted_files.zip"'

            return response
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})

