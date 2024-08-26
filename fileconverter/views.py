import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm

def format_row(row):
    date_field = str(int(row['Date'])) if not pd.isna(row['Date']) else '0'.ljust(18)
    code_field = str(int(row['Account Code'])) if not pd.isna(row['Account Code']) else '0'.ljust(7)
    amount_field = str(int(row['Amount'])) if not pd.isna(row['Amount']) else '0'.rjust(42)
    currency_field = str(row['Currency']) if not pd.isna(row['Currency']) else '0'.rjust(4)
    
    date_field = date_field.ljust(18)
    code_field = code_field.ljust(7)
    amount_field = amount_field.rjust(42)
    currency_field = currency_field.rjust(4)
    
    return f"{date_field}{code_field}{amount_field} {currency_field}"

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Read the Excel file
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            
            # Format the rows
            formatted_rows = "\n".join(df.apply(format_row, axis=1))
            
            # Create an HTTP response with the formatted text file
            response = HttpResponse(formatted_rows, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="formatted_output.txt"'
            return response
    else:
        form = UploadFileForm()
    
    return render(request, 'upload.html', {'form': form})
