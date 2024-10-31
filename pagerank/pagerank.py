import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    # ranks = iterate_pagerank(corpus, DAMPING)
    # print(f"PageRank Results from Iteration")
    # for page in sorted(ranks):
    #     print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor)-> dict[str,float]:
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    '''all pages will have an initial prob of (1-d)/N, where N is the total number of pages in the corpus. That's what's being taken care off here.'''
    init_prob = (1-damping_factor)/len(corpus)

    '''Next, you need to calculate the probability of choosing any of the linked pages on the current page.'''
    if len(corpus[page])>0: #assuming the page has linked pages
        prob = damping_factor/len(corpus[page])
        final_prob = init_prob+prob
        # print(f'This is init_prob:{init_prob}, this is prob:{prob}, and this is final_prob:{final_prob}')

    elif len(corpus[page])==0:
        '''Now if the page has no linked pages'''
        prob = damping_factor/len(corpus)
        final_prob = init_prob+prob
        # print(f'This is init_prob:{init_prob}, this is prob:{prob}, and this is final_prob:{final_prob}')

    transition = {}
    for item in corpus:
        if item in corpus[page]:
            transition[item]=final_prob
        else:
            transition[item]=init_prob

    return transition

    # raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n)->dict[str, float]:
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # 1. initially sample a page at random
    # Do the following until the number of samples has been reached:
    # 2. pass that page to the transition model to get the probabilities for the next sample
    # 3. sample a page at random from this transition model, based on the probabilities returned.
    visits = {page_name:0 for page_name in corpus}

    current_page = random.choice(list(visits.keys()))

    count = 1
    while count < n:
        visits[current_page]+=1
        trans_model = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(list(trans_model.keys()), list(trans_model.values()), k=1)[0]

        count+=1

    for page in visits:
        visits[page]/=n 
    return visits



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    page_rank={page:1/len(corpus) for page in corpus}

    for i in range(1000):
        for page in corpus:
            page_rank[page] = (1-damping_factor)/len(corpus) + sum([damping_factor*(page_rank[i]/len(corpus[i])) for i in corpus if page in corpus[i]])

    return page_rank


    # raise NotImplementedError


if __name__ == "__main__":
    main()
    # expected pagerank 1 to be in range [0.16991, 0.26991], got 0.4625 instead
    # print(f"This is iterate_pagerank:\n {iterate_pagerank({'1': {'2'}, '2': {'3', '1'}, '3': {'2', '4'}, '4': {'2'}}, 0.85)}")
    # print(f"This is sample_pagerank:\n {sample_pagerank({'1': {'2'}, '2': {'3', '1'}, '3': {'2', '4'}, '4': {'2'}}, 0.85, 1000)}")