import collections
import random

from vecanalysis.representations.explicit import Explicit

class SequentialExplicit:

    def __init__(self, input_dir,  years, restricted_contexts=None, normalize=True):
        self.embeds = collections.OrderedDict()
        if restricted_contexts == None:
            restricted_contexts = collections.defaultdict(lambda : None)
        for year in years:
            self.embeds[year] = Explicit.load(input_dir + "/" + str(year) + ".bin", normalize=normalize, restricted_context=restricted_contexts[year])

    @classmethod
    def from_ordered_dict(cls, year_embeds):
        new_seq_embeds = cls([])
        new_seq_embeds.embeds = year_embeds
        return new_seq_embeds

    def get_time_sims(self, word1, word2):
       time_sims = collections.OrderedDict()
       for year, embed in self.embeds.iteritems():
           time_sims[year] = embed.similarity(word1, word2)
       return time_sims

    def get_embed(self, year):
        return self.embeds[year]

    def get_seq_neighbour_set(self, word, n=3):
        neighbour_set = set([])
        for embed in self.embeds.itervalues():
            closest = embed.closest(word, n=n)
            for _, neighbour in closest:
                neighbour_set.add(neighbour)
        return neighbour_set

    def get_ambassador_list(self, word, start_year, end_year, num_a=5, n=50, first_order=True):
        neighbours = collections.defaultdict(float)
        for year in xrange(start_year, end_year + 1):
            embed = self.get_embed(year)
            if first_order:
                closest = embed.closest_first_order(word, n=n+1)
            else:
                closest = embed.closest(word, n=n+1)
            for score, neighbour in closest:
                if neighbour != word:
                    neighbours[neighbour] += score
        return sorted(neighbours, key = lambda neighbour : neighbours[neighbour], reverse=True)[:num_a]

    def get_word_subembeds(self, word, n=3, num_rand=None, word_list=None):
        if word_list == None:
            word_set = self.get_seq_neighbour_set(word, n=n)
            if num_rand != None:
                word_set = word_set.union(set(random.sample(self.embeds.values()[-1].iw, num_rand)))
            word_list = list(word_set)
        year_subembeds = collections.OrderedDict()
        for year,embed in self.embeds.iteritems():
            year_subembeds[year] = embed.get_subembed(word_list)
        return SequentialExplicit.from_ordered_dict(year_subembeds)
