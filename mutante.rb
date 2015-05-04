
def locate(int, ary)
  # Returns the index of the first element of ary that is greater than int.
  return nil if int < 1
  return nil if int > ary.last
  target = int
  base = 0
  ary.each_with_index do |x, i|
    return i if target <= x
  end
end

def shuffle(ary)
  old = ary
  # Store the aggregated votes/cumulative percentages
  cumu = old.map.with_index { |_, i| ary.first(i+1).reduce(:+) }
  sum = cumu.last
  # Create a new array, by randomly drawing 'sum" elements from the original array.
  new = ary.map { 0 }
  sum.times do
    vote = locate(rand(sum)+1, cumu)
    new[vote] +=1
  end
  new
end


