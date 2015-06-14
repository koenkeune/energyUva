import pandas

def save_file(df, path):
	df.to_csv(path, index=False)