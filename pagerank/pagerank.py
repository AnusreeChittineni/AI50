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
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


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


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Initializes dictionary for probability distributuion
    prob_distri = dict()

    # Initializes list of keys in the corpus, this is so you know the number of pages in the corpus
    keys = list(corpus.keys())

    # Initializes the variable pages_linked to the value of the key page in the corpus dictionary, this will tell what pages are linked from the current one
    pages_linked = corpus[page]

    # Initializes r to the probability of choosing any of the page in the corpus
    r = (1 - damping_factor) / len(keys)

    # Initializes n_links to the number of pages linked on the current page
    n_links = len(pages_linked)

    # Checks if n_links is 0
    if n_links == 0:

        # If so, then assume the page is linked to all the pages in the corpus, including itself and set p to the probability of selected one of them
        p = damping_factor / len(keys)

    else:

        # Else, set p to the probability selecting a page from the ones linked to the current page
        p = damping_factor / n_links

    # Loop through each key in keys to set the values for each key
    for key in keys:

        # Checks if key is a linked paged
        if key in pages_linked:

            # If so then set probability distributuion to the total of r + p
            prob_distri[key] = p + r

        else:

            # Else set probability distribution to just r
            prob_distri[key] = r

    # Returns final probability distribution dictionary
    return prob_distri


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initializes dictionary used to display page rankings
    pagerank = dict()

    # Initializes empty list used to store the samples used to rank the pages
    samples = []

    # Initializes first sample by random selection
    current_page = random.choice(list(corpus.keys()))

    # Adds current page to list of samples
    samples.append(current_page)

    # Repeats a proccess n - 1 times in order to produce n total samples
    for i in range(n - 1):

        # Calculates the probability distribution for the current page using the transition model function
        prob_distri = transition_model(corpus, current_page, damping_factor)

        # Initializes an empty list to store the probability distribution values
        probs = []

        # Loops through each key in prob_distri and adds the value to probs
        for key in prob_distri.keys():

            probs.append(prob_distri[key])

        # Sets a new current page based on a random choice that uses the new weighted probability scale
        # You have to use the pop() because random.choices returns a list
        current_page = random.choices(list(prob_distri.keys()), weights=probs, k=1).pop()

        # Add the new current page to samples
        samples.append(current_page)

    # Loops through each key in the corpus
    for key in corpus.keys():

        # Sets the pagerank for current key to (the total number of times the key showed of in samples / the total number of samples)
        pagerank[key] = samples.count(key)/n

    # Returns the final pagerank dictionary derived from sampling
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initializes dictionary used to display page rankings
    pagerank = dict()

    # Initializes N to the total number of pages in the corpus
    N = len(corpus)

    # Determines the probability
    prob_i = 1/N

    # Loops through each page in the corpus to initialize the probability distribution for each page
    for page in corpus:

        # Each page is initialized to the same probability of being picked
        pagerank[page] = prob_i

    # Initializes variable to track probabilty change, sets to 1 to ensure algorithm enters while loop
    prob_change = 1

    # While prob_change is greater than 0.001, continue iterating through the algorithm and changing the probability distribution
    while prob_change > 0.001:

        # Establishes a copy of current pageranks to use to caculate the probability change after calculating the new pagerankings
        old_pagerank = pagerank.copy()

        # Loops through each page in the corpus and calculates it's probability of being selected
        for page in pagerank:

            # Initializes an empty list to store the pages that house a link to another page
            parent_pages = []

            # Loops through the corpus to determine the pages that link to the current page
            for link in corpus:

                # Checks If cuurent page is linked on a page
                if page in corpus[link]:

                    # If so then add page the current page is linked on to the parent_pages list
                    parent_pages.append(link)

            # Initializes value of the first part of the iteration formula
            first_condition = (1 - damping_factor) / N

            # Initializes an empty list to store the values used in the summation at the end of the iteration formula
            second_condition = []

            # Checks to make sure parent_pages is not empty
            if len(parent_pages) != 0:

                # If not then loop through each page in parent_pages
                for parent_page in parent_pages:

                    # Initializes NumLinks to the number links housed on parent_page
                    NumLinks = len(corpus[parent_page])

                    # Initializes the probability of selecting each linked page by dividing the old pagerank of the parent page by the number of links of the page
                    probability = old_pagerank[parent_page] / NumLinks

                    # Adds the probability to second_condition
                    second_condition.append(probability)

            # Reinitializes second_condition to the sum of all the values in second_condition
            second_condition = sum(second_condition)

            # Calculates the new pagerank using the iteration formula
            pagerank[page] = first_condition + (damping_factor * second_condition)

            # Reassigns the value of prob_change by calculating the change in probability by subtracting th old probability from the new one and taking the absolute value
            prob_change = abs(pagerank[page] - old_pagerank[page])

    # Returns the final pagerank dictionary derived through iteration
    return pagerank


if __name__ == "__main__":
    main()
