from torchtext import data, datasets


class DataLoader(object):
    '''
    Data loader class to load text file using torchtext library.
    '''

    def __init__(self, train_fn, valid_fn, 
                 batch_size=64, 
                 device=-1, 
                 max_vocab=999999, 
                 min_freq=1,
                 use_eos=False, 
                 shuffle=True
                 ):
        '''
        DataLoader initialization.
        :param train_fn: Train-set filename
        :param valid_fn: Valid-set filename
        :param batch_size: Batchify data fot certain batch size.
        :param device: Device-id to load data (-1 for CPU)
        :param max_vocab: Maximum vocabulary size
        :param min_freq: Minimum frequency for loaded word.
        :param use_eos: If it is True, put <EOS> after every end of sentence.
        :param shuffle: If it is True, random shuffle the input data.
        '''
        super(DataLoader, self).__init__()

        # Define field of the input file.
        # The input file consists of two fields.
        self.label = data.Field(sequential=False,
                                use_vocab=True,
                                unk_token=None
                                )
        self.text = data.Field(use_vocab=True, 
                               batch_first=True, 
                               include_lengths=False, 
                               eos_token='<EOS>' if use_eos else None
                               )

        # Those defined two columns will be delimited by TAB.
        # Thus, we use TabularDataset to load two columns in the input file.
        # We would have two separate input file: train_fn, valid_fn
        # Files consist of two columns: label field and text field.
        train, valid = data.TabularDataset.splits(path='', 
                                                  train=train_fn, 
                                                  validation=valid_fn, 
                                                  format='tsv', 
                                                  fields=[('label', self.label),
                                                          ('text', self.text)
                                                          ]
                                                  )

        # Those loaded dataset would be feeded into each iterator:
        # train iterator and valid iterator.
        # We sort input sentences by length, to group similar lengths.
        self.train_iter, self.valid_iter = data.BucketIterator.splits((train, valid), 
                                                                      batch_size=batch_size, 
                                                                      device='cuda:%d' % device if device >= 0 else 'cpu', 
                                                                      shuffle=shuffle,
                                                                      sort_key=lambda x: len(x.text),
                                                                      sort_within_batch=True
                                                                      )

        # At last, we make a vocabulary for label and text field.
        # It is making mapping table between words and indice.
        self.label.build_vocab(train)
        self.text.build_vocab(train, max_size=max_vocab, min_freq=min_freq)
        