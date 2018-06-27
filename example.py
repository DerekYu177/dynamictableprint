from dynamictableprint import DynamicTablePrint
import pandas as pd

d = {
    'names': [
        "Albert Einstein",
        "Issac Newton",
        "Stephen Hawkings"
    ],
    'places': [
        "Ulm, Germany",
        "Wolsthorpe Manor, United Kingdom",
        "Oxford, United Kingdom"
    ],
    'Foods': [
        "Spaghetti",
        "Pasta",
        "Noodles"
    ]
}
data_frame = pd.DataFrame(data=d)

dtp = DynamicTablePrint(data_frame, angel_column='Foods', squish_column='places')
dtp.config.banner = 'Things!'
dtp.write_to_screen()
