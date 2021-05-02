class PhonotacticError(Exception):
  pass
class Syllable:
  def __init__(self, vowel):
    self.onsets = []
    self.vowel = vowel
    self.codas = []
  def __str__(self):
    onset_str = ' '.join(self.onsets) + ' ' if len(self.onsets) != 0 else ''
    codas_str = ' ' + ' '.join(self.codas) if len(self.codas) != 0 else ''
    return onset_str + self.vowel + codas_str
  def add_onset(self, onset):
    if len(self.onsets) == 3:
      raise PhonotacticError('Already at 3 onsets')
    self.onsets.insert(0, onset)
  def add_coda(self, coda):
    if len(self.codas) == 5:
      raise PhonotacticError('Already at 5 codas')
    self.codas.append(coda)
  def remove_onset(self):
    if len(self.onsets) == 0:
      raise PhonotacticError('No onsets')
    self.onsets.remove(0)
  def remove_coda(self):
    if len(self.codas) == 0:
      raise PhonotacticError('No codas')
    self.codas.pop()
