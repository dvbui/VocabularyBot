def register_message():
    mess = "```\n"
    mess += "Registration Phase\n"
    mess += "Generating a new block in 30 seconds\n"
    mess += "Type \"olym register\" to solve this block\n"
    mess += "To stop receiving clues and unregister, type \"olym stop\".\n"
    mess += "```\n"
    return mess


def rule_message():
    mess = "```\n"
    mess += "Luật thi Vượt chướng ngại vật\n"
    mess += "Các thí sinh cùng trả lời 4 câu hỏi.\n"
    mess += "Nội dung và câu trả lời của mỗi câu hỏi là các gợi ý để tìm một từ chìa khóa (keyword).\n"
    mess += "Các thí sinh trả lời 4 câu hỏi bằng cách gõ câu trả lời (không cần kèm theo tiền tố nào)\n"
    mess += "Thời gian suy nghĩ của mỗi câu hỏi là 25 giây một câu.\n"
    mess += "Trả lời đúng mỗi câu hỏi, thí sinh được 1 điểm.\n"
    mess += "Thí sinh có thể trả lời từ chìa khóa bất cứ lúc nào bằng cách gõ olym solve [từ chìa khóa]\n"
    mess += "(trừ lúc chờ câu hỏi xuất hiện và lúc chờ chấm điểm các đáp án)\n"
    mess += "Trả lời đúng từ chìa khóa trong vòng 1 câu hỏi được 8 điểm, "
    mess += "trong vòng 2 câu hỏi được 6 điểm, 3 câu hỏi được 4 điểm, 4 câu hỏi được 2 điểm\n"
    mess += "Nếu trong vòng 4 câu hỏi không có thí sinh nào trả lời được từ chìa khóa, định nghĩa của từ chìa khóa "
    mess += "sẽ xuất hiện. Thí sinh trả lời đúng từ chìa khóa sau khi định nghĩa xuất hiện được 1 điểm.\n"
    mess += "Lưu ý: Thí sinh trả lời sai từ chìa khóa sẽ bị loại khỏi phần chơi này"
    mess += "(Câu trả lời được coi là đúng nếu có số chữ cái bằng với số chữ cái được cho trước và đồng nghĩa với đáp án.)"
    mess += "(Nếu câu trả lời cho từ chìa khóa của thí sinh không khớp với từ chìa khóa nhưng không đồng nghĩa "
    mess += "thì thí sinh vẫn giành điểm nhưng trò chơi không kết thúc)\n"
    mess += "```\n"
    return mess


def question_message(question, index="", number_of_character="",final_clue=False):
    mess = "```\n"
    mess += "\n"
    mess += "Clue {} ({} characters):\n".format(index, number_of_character)
    mess += question+"\n"
    mess += "\n"
    mess += "You have 25 seconds to answer this clue.\n"
    if not final_clue:
        mess += "Type your best answer (and only your answer) to answer this clue.\n"
        mess += "To guess the keyword, type \"olym solve [keyword]\"\n"
    else:
        mess += "The answer for this clue is the keyword.\n"
        mess += "Type your best guess (and only your guess) for the keyword.\n"
    mess += "```"
    return mess


def block_end_message(word, long_definition, winner):
    mess = "```\n"
    if winner != "":
        mess += "{} solved this block!".format(winner)+"\n\n"
    mess += "The keyword is "+word+"\n"
    mess += "\n"
    mess += "From Vocabulary.com:\n"
    mess += long_definition + "\n"
    mess += "```\n"
    return mess


def keyword_message(length, not_keywords=""):
    mess = "```\n"
    mess += "The keyword has {}".format(length)+" characters.\n"
    if not_keywords != "":
        mess += "The keyword is not:{}".format(not_keywords)+"\n"
    mess += "```\n"
    return mess


def ranklist_message(user_list):
    mess = "```\n"
    mess += "Name \t\t Score\n"
    for user in user_list:
        mess += str(user)+" \t\t "+str(user_list[user]["score"])+"\n"
    mess += "```\n"
    return mess


def show_user_answer(user_list):
    mess = "```\n"
    mess += "Name \t\t Answer\n"
    for user in user_list:
        if user_list[user]["answer"] != "":
            mess += str(user)+" \t\t "+str(user_list[user]["answer"])+"\n"
    mess += "```\n"
    return mess
