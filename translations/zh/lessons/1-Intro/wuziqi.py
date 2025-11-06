"""
五子棋人机对战游戏
使用评分搜索算法选择最优落子位置
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

class GomokuGame:
    def __init__(self, board_size=15):
        """
        初始化五子棋游戏
        
        Args:
            board_size: 棋盘大小，默认15x15
        """
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 1  # 1=玩家(黑), 2=AI(白)
        self.game_over = False
        
        # 棋型评分权重
        # 进攻评分：己方形成棋型的得分
        self.attack_scores = {
            'five': 100000,           # 连五 (必胜)
            'live_four': 50000,       # 活四 (对方必须防守，几乎必胜，权重大幅提高)
            'live_three': 5000,       # 活三 (可以形成多种攻势)
            'sleep_four': 1000,       # 眠四 (一侧被阻挡，威胁较大但仍需防守)
            'live_two': 200,          # 活二 (比眠三重要)
            'sleep_three': 50,        # 眠三 (降低权重)
            'sleep_two': 1,           # 眠二
        }
        
        # 防守评分：对方形成棋型的得分（我应该防守的优先级）
        self.defense_scores = {
            'five': 100000,           # 对方连五 (必须防守)
            'live_four': 80000,       # 对方活四 (必须防守，权重大幅提高，接近连五)
            'live_three': 7500,       # 对方活三 (必须防守，权重提高)
            'sleep_four': 1500,       # 对方眠四 (需要防守)
            'live_two': 300,          # 对方活二 (比眠三重要)
            'sleep_three': 75,        # 对方眠三 (降低权重)
            'sleep_two': 2,           # 对方眠二
        }
        
        # 初始化GUI
        self.setup_gui()
        
    def setup_gui(self):
        """设置图形界面"""
        self.root = tk.Tk()
        self.root.title("五子棋 - 人机对战")
        self.root.resizable(False, False)
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            width=660,
            height=680,
            bg='#DEB887'
        )
        self.canvas.pack()
        
        # 绘制棋盘
        self.draw_board()
        
        # 绑定鼠标点击事件
        self.canvas.bind('<Button-1>', self.on_click)
        
        # 创建信息标签
        self.info_label = tk.Label(
            self.root,
            text="黑方先行，请下子",
            font=('Arial', 14)
        )
        self.info_label.pack()
        
        # 重新开始按钮
        restart_btn = tk.Button(
            self.root,
            text="重新开始",
            command=self.restart_game,
            font=('Arial', 12)
        )
        restart_btn.pack(pady=5)
        
    def draw_board(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        
        # 绘制网格线
        for i in range(self.board_size):
            # 横线
            y = 40 + i * 40
            self.canvas.create_line(40, y, 40 + (self.board_size - 1) * 40, y, width=1)
            
            # 竖线
            x = 40 + i * 40
            self.canvas.create_line(x, 40, x, 40 + (self.board_size - 1) * 40, width=1)
        
        # 绘制天元和星位
        star_positions = [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]
        for x, y in star_positions:
            px = 40 + x * 40
            py = 40 + y * 40
            self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill='black')
        
        # 绘制棋子
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 1:  # 玩家(黑)
                    self.draw_piece(j, i, 'black')
                elif self.board[i][j] == 2:  # AI(白)
                    self.draw_piece(j, i, 'white')
    
    def draw_piece(self, col, row, color):
        """绘制棋子"""
        x = 40 + col * 40
        y = 40 + row * 40
        fill_color = 'black' if color == 'black' else 'white'
        outline_color = 'white' if color == 'black' else 'black'
        
        self.canvas.create_oval(
            x - 15, y - 15,
            x + 15, y + 15,
            fill=fill_color,
            outline=outline_color,
            width=2
        )
    
    def on_click(self, event):
        """处理鼠标点击事件"""
        if self.game_over:
            return
        
        # 将像素坐标转换为棋盘坐标
        col = round((event.x - 40) / 40)
        row = round((event.y - 40) / 40)
        
        # 检查坐标是否有效
        if not (0 <= col < self.board_size and 0 <= row < self.board_size):
            return
        
        # 检查位置是否已落子
        if self.board[row][col] != 0:
            return
        
        # 玩家下棋
        if self.current_player == 1:
            self.board[row][col] = 1
            self.draw_board()
            
            # 检查玩家是否获胜
            if self.check_win(row, col, 1):
                self.game_over = True
                messagebox.showinfo("游戏结束", "恭喜！你赢了！")
                self.info_label.config(text="黑方获胜！")
                return
            
            self.info_label.config(text="白方思考中...")
            self.root.update()
            
            # AI下棋
            self.current_player = 2
            ai_move = self.get_ai_move()
            if ai_move:
                ai_row, ai_col = ai_move
                self.board[ai_row][ai_col] = 2
                self.draw_board()
                
                # 检查AI是否获胜
                if self.check_win(ai_row, ai_col, 2):
                    self.game_over = True
                    messagebox.showinfo("游戏结束", "AI获胜！")
                    self.info_label.config(text="白方获胜！")
                    return
                
                self.current_player = 1
                self.info_label.config(text="黑方行棋")
            else:
                self.game_over = True
                messagebox.showinfo("游戏结束", "平局！")
                self.info_label.config(text="平局")
    
    def check_win(self, row, col, player):
        """
        检查指定位置是否形成五连
        
        Args:
            row: 行号
            col: 列号
            player: 玩家编号 (1或2)
            
        Returns:
            bool: 是否形成五连
        """
        directions = [
            (0, 1),   # 横向
            (1, 0),   # 纵向
            (1, 1),   # 主对角线
            (1, -1)   # 副对角线
        ]
        
        for dr, dc in directions:
            count = 1  # 当前棋子
            
            # 向一个方向延伸
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 
                   0 <= c < self.board_size and 
                   self.board[r][c] == player):
                count += 1
                r, c = r + dr, c + dc
            
            # 向相反方向延伸
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 
                   0 <= c < self.board_size and 
                   self.board[r][c] == player):
                count += 1
                r, c = r - dr, c - dc
            
            if count >= 5:
                return True
        
        return False
    
    def get_ai_move(self):
        """
        使用评分搜索算法选择AI的落子位置
        
        Returns:
            Tuple[int, int]: AI落子的行号和列号
        """
        best_score = float('-inf')
        best_move = None
        
        # 生成候选位置（只考虑已有棋子周围的空位）
        candidates = self.get_candidate_positions()
        
        if not candidates:
            # 如果没有候选位置，选择棋盘中心
            return (self.board_size // 2, self.board_size // 2)
        
        # 评估每个候选位置
        for row, col in candidates:
            # 尝试在此位置落子
            self.board[row][col] = 2
            
            # 计算评分
            score = self.evaluate_position(row, col, 2)
            
            # 撤销落子
            self.board[row][col] = 0
            
            # 更新最佳位置
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        # 调试输出
        if best_move:
            print(f"AI选择位置: ({best_move[0]}, {best_move[1]}), 得分: {best_score}")
        
        return best_move
    
    def get_candidate_positions(self):
        """
        生成候选落子位置（已有棋子周围的空位）
        
        Returns:
            List[Tuple[int, int]]: 候选位置列表
        """
        candidates = set()
        
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] != 0:
                    # 检查周围8个方向
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = i + di, j + dj
                            if (0 <= ni < self.board_size and 
                                0 <= nj < self.board_size and 
                                self.board[ni][nj] == 0):
                                candidates.add((ni, nj))
        
        # 如果棋盘为空，返回中心位置
        if not candidates:
            candidates.add((self.board_size // 2, self.board_size // 2))
        
        return list(candidates)
    
    def evaluate_position(self, row, col, player):
        """
        评估某个位置的得分
        综合考虑：1) 我下在这里对我进攻的好处
                  2) 我下在这里对防守的好处（阻止对方）
                  3) 组合棋型奖励（如双眠四、双活三等）
        
        Args:
            row: 行号
            col: 列号
            player: 玩家编号
            
        Returns:
            int: 综合位置得分
        """
        attack_score = 0  # 进攻得分：我下这里对我进攻的好处
        defense_score = 0  # 防守得分：我下这里对防守的好处（阻止对方威胁）
        
        # 评估4个方向的棋型
        directions = [
            (0, 1),   # 横向
            (1, 0),   # 纵向
            (1, 1),   # 主对角线
            (1, -1)   # 副对角线
        ]
        
        # 记录每个方向的得分，用于检测组合棋型
        attack_scores_by_dir = []
        defense_scores_by_dir = []
        
        for dr, dc in directions:
            # 评估己方棋型（进攻得分）
            my_pattern = self.get_pattern(row, col, dr, dc, player)
            my_score = self.get_pattern_score(my_pattern, player, True)
            attack_score += my_score
            attack_scores_by_dir.append(my_score)
            
            # 评估对方棋型（防守得分：如果不下这里，对方的威胁程度）
            opponent = 3 - player  # 对方玩家编号
            opp_pattern = self.get_pattern(row, col, dr, dc, opponent)
            opp_score = self.get_pattern_score(opp_pattern, opponent, False)
            defense_score += opp_score
            defense_scores_by_dir.append(opp_score)
            
            # 调试输出（找到高分位置时）
            if my_score >= 1000 or opp_score >= 1000:
                dir_name = ["横向", "纵向", "主对角线", "副对角线"][directions.index((dr, dc))]
                print(f"  方向{dir_name}: 己方pattern={my_pattern} 进攻得分={my_score}, "
                      f"对方pattern={opp_pattern} 防守得分={opp_score}")
        
        # 检测组合棋型并给予额外奖励
        combo_bonus = self.calculate_combo_bonus(attack_scores_by_dir, defense_scores_by_dir)
        
        # 综合得分：进攻得分 + 防守得分 + 组合奖励
        total_score = attack_score + defense_score + combo_bonus
        
        # 调试输出（显示综合得分详情）
        if attack_score >= 1000 or defense_score >= 1000 or combo_bonus > 0:
            print(f"  位置({row},{col}): 进攻得分={attack_score}, 防守得分={defense_score}, "
                  f"组合奖励={combo_bonus}, 综合得分={total_score}")
        
        return total_score
    
    def calculate_combo_bonus(self, attack_scores, defense_scores):
        """
        计算组合棋型的额外奖励
        
        组合棋型说明：
        - 双活四：两个方向都是活四，必胜
        - 双眠四：两个方向都是眠四，几乎必胜（对方只能防守一个）
        - 活四+眠四：一个活四和一个眠四的组合
        - 双活三：两个方向都是活三，威胁很大
        - 活三+眠四：一个活三和一个眠四的组合
        
        Args:
            attack_scores: 4个方向的进攻得分列表
            defense_scores: 4个方向的防守得分列表
            
        Returns:
            int: 组合奖励分数
        """
        bonus = 0
        
        # 获取评分阈值（用于判断棋型）
        live_four_score = self.attack_scores['live_four']
        sleep_four_score = self.attack_scores['sleep_four']
        live_three_score = self.attack_scores['live_three']
        
        # 统计进攻方的组合棋型
        live_four_count = sum(1 for score in attack_scores if score >= live_four_score * 0.9)
        sleep_four_count = sum(1 for score in attack_scores 
                              if sleep_four_score * 0.9 <= score < live_four_score * 0.9)
        live_three_count = sum(1 for score in attack_scores 
                               if live_three_score * 0.9 <= score < sleep_four_score * 0.9)
        
        # 双活四：必胜，给予极高奖励
        if live_four_count >= 2:
            bonus += 50000  # 相当于又一个活四的奖励
            print(f"  ⚡检测到双活四！奖励+50000")
        
        # 活四+眠四：几乎必胜
        elif live_four_count >= 1 and sleep_four_count >= 1:
            bonus += 30000  # 很高奖励
            print(f"  ⚡检测到活四+眠四组合！奖励+30000")
        
        # 双眠四：对方只能防守一个，几乎必胜
        elif sleep_four_count >= 2:
            bonus += 25000  # 很高的奖励
            print(f"  ⚡检测到双眠四！奖励+25000")
        
        # 双活三：威胁很大
        elif live_three_count >= 2:
            bonus += 8000  # 较高的奖励
            print(f"  ⚡检测到双活三！奖励+8000")
        
        # 活三+眠四：威胁较大
        elif live_three_count >= 1 and sleep_four_count >= 1:
            bonus += 5000  # 中等奖励
            print(f"  ⚡检测到活三+眠四组合！奖励+5000")
        
        # 防守方的组合威胁也需要额外重视
        defense_live_four = self.defense_scores['live_four']
        defense_sleep_four = self.defense_scores['sleep_four']
        defense_live_three = self.defense_scores['live_three']
        
        defense_live_four_count = sum(1 for score in defense_scores 
                                     if score >= defense_live_four * 0.9)
        defense_sleep_four_count = sum(1 for score in defense_scores 
                                       if defense_sleep_four * 0.9 <= score < defense_live_four * 0.9)
        
        # 对方双活四：必须防守，极高优先级
        if defense_live_four_count >= 2:
            bonus += 40000  # 防守奖励
            print(f"  ⚠️检测到对方双活四威胁！防守奖励+40000")
        
        # 对方活四+眠四：必须防守
        elif defense_live_four_count >= 1 and defense_sleep_four_count >= 1:
            bonus += 25000  # 防守奖励
            print(f"  ⚠️检测到对方活四+眠四威胁！防守奖励+25000")
        
        # 对方双眠四：需要防守
        elif defense_sleep_four_count >= 2:
            bonus += 15000  # 防守奖励
            print(f"  ⚠️检测到对方双眠四威胁！防守奖励+15000")
        
        return bonus
    
    def get_pattern(self, row, col, dr, dc, player):
        """
        获取某个方向的棋型
        
        Args:
            row: 行号
            col: 列号
            dr: 行方向增量
            dc: 列方向增量
            player: 玩家编号
            
        Returns:
            str: 棋型字符串，格式为"棋子序列"
        """
        pattern = []
        
        # 向一个方向延伸
        for i in range(4):
            r, c = row + dr * (i + 1), col + dc * (i + 1)
            if 0 <= r < self.board_size and 0 <= c < self.board_size:
                pattern.append(str(self.board[r][c]))
            else:
                pattern.append('9')  # 边界标记为9（防止与玩家编号冲突）
        
        pattern.reverse()
        pattern.append(str(player))
        
        # 向相反方向延伸
        for i in range(4):
            r, c = row - dr * (i + 1), col - dc * (i + 1)
            if 0 <= r < self.board_size and 0 <= c < self.board_size:
                pattern.append(str(self.board[r][c]))
            else:
                pattern.append('9')  # 边界
        
        return ''.join(pattern)
    
    def get_pattern_score(self, pattern, player, is_attacking):
        """
        根据棋型计算得分
        
        Args:
            pattern: 棋型字符串
            player: 当前评估的玩家编号（1或2）
            is_attacking: 是否为攻击（True=攻击，False=防守）
            
        Returns:
            int: 得分
        """
        # 将棋盘转化为统一格式：'X'表示我方棋子，'O'表示对方棋子，'.'表示空格
        # player表示当前评估的玩家
        my_char = str(player)
        opp_char = str(3 - player)
        
        # 先替换边界标记'9'为'O'，因为边界视为对方棋子（无法延伸）
        pattern = pattern.replace('9', 'O')
        # 再替换玩家棋子
        pattern = pattern.replace(my_char, 'X').replace(opp_char, 'O').replace('0', '.')
        
        # pattern格式：前4位(反向) + 当前位(中心，index=4) + 后4位(正向) = 9位
        # 从中心位置向两侧统计连续棋子
        center_idx = 4
        
        # 检查中心位置是否是X（应该是，因为我们在评估落子后的棋型）
        if pattern[center_idx] != 'X':
            return 0  # 中心位置不是X，返回0分
        
        # 从中心向左侧（反向）统计连续X
        left_count = 0
        for i in range(center_idx - 1, -1, -1):
            if pattern[i] == 'X':
                left_count += 1
            else:
                break
        
        # 从中心向右侧（正向）统计连续X
        right_count = 0
        for i in range(center_idx + 1, len(pattern)):
            if pattern[i] == 'X':
                right_count += 1
            else:
                break
        
        # 总连续数 = 左侧 + 中心(1) + 右侧
        total_consecutive = left_count + 1 + right_count
        
        # 找到连续X的起始和结束位置
        start_idx = center_idx - left_count
        end_idx = center_idx + right_count
        
        # 根据进攻或防守选择不同的评分表
        scores = self.attack_scores if is_attacking else self.defense_scores
        
        # 检查连五
        if total_consecutive >= 5:
            return scores['five']
        
        # 检查活四/眠四 (连续4个子，检查两端)
        if total_consecutive == 4:
            # 检查左边（连续X的左侧）
            left_ok = False
            if start_idx > 0:
                if pattern[start_idx - 1] == '.':
                    left_ok = True  # 左边是空格
            # 注意：如果start_idx == 0，说明到达边界，边界不算空格（已替换为'O'）
            
            # 检查右边（连续X的右侧）
            right_ok = False
            if end_idx + 1 < len(pattern):
                if pattern[end_idx + 1] == '.':
                    right_ok = True  # 右边是空格
            # 注意：如果end_idx + 1 >= len(pattern)，说明到达边界
            
            if left_ok and right_ok:
                return scores['live_four']  # 活四：两侧都是空格，可以形成两个活四点
            elif left_ok or right_ok:
                # 眠四：只有一侧是空格，另一侧被对方棋子或边界阻挡
                if 'sleep_four' in scores:
                    return scores['sleep_four']
                else:
                    # 如果没有定义眠四，使用活四的一半权重作为降级处理
                    return scores['live_four'] // 2
            else:
                # 死四：两侧都被阻挡（实际上无法形成五连，但可能仍有一定威胁）
                return scores['live_four'] // 4
        
        # 检查活三/眠三 (连续3个子，检查两端及扩展空间)
        if total_consecutive == 3:
            # 检查左边（连续X的左侧）
            left_has_space = False
            if start_idx > 0:
                if pattern[start_idx - 1] == '.':
                    left_has_space = True  # 左边是空格
            
            # 检查右边（连续X的右侧）
            right_has_space = False
            if end_idx + 1 < len(pattern):
                if pattern[end_idx + 1] == '.':
                    right_has_space = True  # 右边是空格
            
            # 检查更远的左边（活三需要两边都有足够的空间形成活四）
            left_has_more_space = False
            if start_idx > 1:
                if pattern[start_idx - 2] == '.':
                    left_has_more_space = True  # 更远的左边是空格
            elif start_idx == 1:
                # 只有一位就到边界了，也算有空间（边界外的空间）
                left_has_more_space = True
            
            # 检查更远的右边
            right_has_more_space = False
            if end_idx + 2 < len(pattern):
                if pattern[end_idx + 2] == '.':
                    right_has_more_space = True  # 更远的右边是空格
            elif end_idx + 2 >= len(pattern) and end_idx + 1 < len(pattern):
                # 只有一位就到边界了，也算有空间
                right_has_more_space = True
            
            # 活三: 至少一端有空格，且该端有足够的扩展空间
            if (left_has_space and left_has_more_space) or (right_has_space and right_has_more_space):
                return scores['live_three']
            elif left_has_space or right_has_space:
                return scores['sleep_three']  # 眠三：只有一侧有空格
            else:
                return 0  # 两端都被阻挡，不是有效的三
        
        # 检查活二 (连续2个子，检查两端)
        if total_consecutive == 2:
            # 检查左边（连续X的左侧）
            left_ok = False
            if start_idx > 0:
                if pattern[start_idx - 1] == '.':
                    left_ok = True  # 左边是空格
            
            # 检查右边（连续X的右侧）
            right_ok = False
            if end_idx + 1 < len(pattern):
                if pattern[end_idx + 1] == '.':
                    right_ok = True  # 右边是空格
            
            if left_ok or right_ok:
                return scores['live_two']
            else:
                return scores['sleep_two']  # 眠二：两端都被阻挡
        
        return 0
    
    def restart_game(self):
        """重新开始游戏"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.draw_board()
        self.info_label.config(text="黑方先行，请下子")
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()


def main():
    """主函数"""
    print("启动五子棋游戏...")
    print("规则说明：")
    print("1. 黑方先行")
    print("2. 率先形成五连的一方获胜")
    print("3. AI使用评分搜索算法选择落子位置")
    print("\n开始游戏！")
    
    game = GomokuGame(board_size=15)
    game.run()


if __name__ == '__main__':
    main()

