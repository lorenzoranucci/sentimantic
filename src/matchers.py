from snorkel.matchers import RegexMatchEach


class GPEMatcher(RegexMatchEach):
    """
    Matches Spans that are the names of locations, as identified by CoreNLP.

    A convenience class for setting up a RegexMatchEach to match spans
    for which each token was tagged as a location.
    """
    def __init__(self, *children, **kwargs):
        kwargs['attrib'] = 'ner_tags'
        kwargs['rgx'] = 'LOCATION|LOC|GPE'
        super(GPEMatcher, self).__init__(*children, **kwargs)


class EventMatcher(RegexMatchEach):
    """
    Matches Spans that are the names of locations, as identified by CoreNLP.

    A convenience class for setting up a RegexMatchEach to match spans
    for which each token was tagged as a location.
    """
    def __init__(self, *children, **kwargs):
        kwargs['attrib'] = 'ner_tags'
        kwargs['rgx'] = 'EVENT'
        super(EventMatcher, self).__init__(*children, **kwargs)

class WorkOfArtMatcher(RegexMatchEach):
    """
    Matches Spans that are the names of locations, as identified by CoreNLP.

    A convenience class for setting up a RegexMatchEach to match spans
    for which each token was tagged as a location.
    """
    def __init__(self, *children, **kwargs):
        kwargs['attrib'] = 'ner_tags'
        kwargs['rgx'] = 'WORK_OF_ART'
        super(WorkOfArtMatcher, self).__init__(*children, **kwargs)

class LanguageMatcher(RegexMatchEach):
    """
    Matches Spans that are the names of locations, as identified by CoreNLP.

    A convenience class for setting up a RegexMatchEach to match spans
    for which each token was tagged as a location.
    """
    def __init__(self, *children, **kwargs):
        kwargs['attrib'] = 'ner_tags'
        kwargs['rgx'] = 'LANGUAGE'
        super(LanguageMatcher, self).__init__(*children, **kwargs)