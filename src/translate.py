import os
import sys

project_root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(project_root_path)

import library.translator as translator
import library.nn_architectures as nn_architectures
import library.preprocessor as preprocessor
import torch

encoder_path = "/Users/morikawakaion/Desktop/nmt/models/transformer_encoder_20250710_132941_158"
decoder_path = "/Users/morikawakaion/Desktop/nmt/models/transformer_decoder_20250710_132941_158"
src_language = "English"

src_seq_len = 55
tgt_seq_len = 68
translator_class = translator.Translator(encoder_path, decoder_path)
hidden_size = 256
encoder = nn_architectures.TransformerEncoder(9783, hidden_size, src_seq_len, num_layer=3, dropout_p=0.3, relposenc=False, linear_hidden_ratio=8)
decoder = nn_architectures.TransformerDecoder(hidden_size, 15532, tgt_seq_len, num_layer=3, dropout_p=0., relposenc=False, linear_hidden_ratio=8)

encoder, decoder = translator_class.load_models(encoder, decoder)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
encoder = encoder.to(device)
decoder = decoder.to(device)
encoder.eval()
decoder.eval()

src_vocab = translator_class.load_vocab("../data/eng_vocab.pkl")
tgt_vocab = translator_class.load_vocab("../data/fra_vocab.pkl")

src_word2idx = src_vocab["word2idx"]
tgt_idx2word = tgt_vocab["idx2word"]

src_text = input(f"Enter a text in {src_language}: ")

standadizer = preprocessor.Standardizer()
src_standadized_text = standadizer.standardize([src_text])

tokenizer = preprocessor.Tokenizer()    
src_tokenized_text = tokenizer.word_tokenize(src_standadized_text, src_seq_len)

indexer = preprocessor.Indexer()
indexer.word2idx = src_word2idx
src_idx = torch.tensor(indexer.text_to_indices(src_tokenized_text, verbose=False)).to(device)

# Pad src_idx to length src_seq_len
if len(src_idx) < src_seq_len:
    padding_length = src_seq_len - len(src_idx[0])
    padding = torch.full((1, padding_length,), 2, dtype=torch.long).to(device)
    src_idx = torch.cat([src_idx, padding], dim=1)

translated_text = translator_class.translate(src_idx, encoder, decoder, tgt_idx2word, transformer=True)
print(f"Translated text: {translated_text}")

