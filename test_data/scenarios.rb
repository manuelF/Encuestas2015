basic_scenario=[45,35,20]

20.times do
  roll=basic_scenario.dup
#  puts "Starting scenario: #{roll}"
  150.times do
    loser=rand(basic_scenario.length)
    winner=rand(basic_scenario.length)
#    puts "#{loser} loses 1 and #{winner} wins 1. | #{roll}"
    roll[loser]-=1
    roll[winner]+=1
  end
  print roll
  print "\n"
end
