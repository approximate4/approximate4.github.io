require 'http'

card_list = File.open("cardlist.txt").readlines.map(&:chomp)

card_list = card_list.map.with_index{ |card, index|
    card_name = card.delete('0-9').gsub(/\(.*?\)/, '').split(" ").join
    if card.match?(/\(.*?\)/)
        card_set = card.match(/\(.*?\)/)[0].delete('()')
        response = HTTP.get("https://api.scryfall.com/cards/named?fuzzy=#{card_name}&set=#{card_set}")
    else
        response = HTTP.get("https://api.scryfall.com/cards/named?fuzzy=#{card_name}")
    end
    searched_card = JSON.parse(response.body)
    sleep(0.1)
    puts "processed card #{index + 1}..."
    if searched_card["card_faces"] && searched_card["highres_image"] == true
        searched_card["card_faces"][0]["image_uris"]["large"] + "|#{searched_card["name"]}"
    elsif searched_card["highres_image"] == true
        searched_card["image_uris"]["large"] + "|#{searched_card["name"]}"
    else
        puts "error on line #{index + 1}. Try removing set or check for spelling"
        ""
    end
}

File.open("images_url.txt", "w") { |file| file.write card_list.reject(&:empty?).join("\n")}