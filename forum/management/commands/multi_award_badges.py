#!/usr/bin/env python
#encoding:utf-8
#-------------------------------------------------------------------------------
# Name:        Award badges command
# Purpose:     This is a command file croning in background process regularly to
#              query database and award badges for user's special acitivities.
#
# Author:      Mike, Sailing
#
# Created:     22/01/2009
# Copyright:   (c) Mike 2009
# Licence:     GPL V2
#-------------------------------------------------------------------------------

from datetime import datetime, date
from django.core.management.base import NoArgsCommand
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from forum.models import *
from forum.const import *
from base_command import BaseCommand
"""
(1, 'purgatory Master', 3, 'purgatory Master', 'delete own more than 3 in favor of the post', 1, 0),
(2, 'pressure on white-collar workers', 3, 'pressure on white-collar', 'delete own more than 3 against the post', 1, 0),
(3, 'good answer', 3, 'good answer', 'answer received more than 10', 1, 0),
(4, 'outstanding issues', 3, 'good question', 'problem received more than 10', 1, 0),
(5, 'critic', 3, 'critic', 'comment more than 10', 0, 0),
(6, 'epidemic', 3, 'epidemic', 'views the problem more than 1,000 people', 1, 0),
(7, 'patrol', 3, 'patrol', 'the first time marked Spam', 0, 0),
(8, 'cleaner', 3, 'cleaner', 'the first revocation vote', 0, 0),
(9, 'critics', 3, 'critic', 'the first time against', 0, 0),
(10, 'Xiao Bian', 3, 'Xiao Bian', 'first edit update', 0, 0),
(11, 'village', 3, 'village', 'first re-label', 0, 0),
(12, 'scholars', 3, 'scholars', 'the first time marked the answer', 0, 0),
(13, 'students', 3, 'Student', 'the first time and have more than one question in favor of', 0, 0),
(14, 'supporters', 3, 'supporters', 'the first time in favor of', 0, 0),
(15, 'Teacher', 3, 'teacher', 'the first time to answer questions and get more than one in favor of', 0, 0),
(16, 'autobiography of the', 3, 'autobiographer', 'fill out all the options the user information', 0, 0),
(17, 'self-taught', 3 'self-taught', 'to answer their own questions and have more than 3 in favor of', 1, 0),
(18, 'the most valuable answer', 1, 'the most valuable answer', 'answered more than 100 times in favor of', 1, 0),
(19, 'the most valuable issue', 1, 'the most valuable issue', 'the problem in favor of more than 100', 1, 0),
(20, 'glamorous', 1, 'glamorous', 'the problem is more than 100 collections', 1, 0),
(21, 'known issue', 1, 'known issue', 'more than 10,000 people views the problem', 1, 0),
(22, 'alpha user', 2, 'alpha user', 'measured during the active users', 0, 0),
(23, 'very good answer', 2, 'excellent answer', 'answered more than 25 times in favor of', 1, 0),
(24, 'great question', 2, 'great question', 'issues more than 25 times in favor of', 1, 0),
(25, 'popular questions', 2, 'popular questions', 'the problem is more than 25 collections', 1, 0),
(26, 'good people', 2, 'good people', 'vote 300 times or more', 0, 0),
(27, 'editorial director', 2, 'editorial director', 'edit posts 100', 0, 0),
(28, 'generalists', 2, 'generalists', 'active in the field in a number of tags', 0, 0),
(29, 'experts', 2, 'experts', 'active in the field in a label superior', 0, 0),
(30, 'old bird', 2, 'old bird', 'active users more than one year', 0, 0),
(31, 'the most talked about issues', 2, 'the most talked about issues', 'views the problem more than 2,500 people', 1, 0),
(32, 'learning family', 2, 'learning family', 'vote for the first answer was more than 10', 0, 0),
(33, 'beta users', 2, 'beta users', 'beta during the active participation', 0, 0),
(34, 'mentor', 2, 'tutor', 'is specified as the best answer, and in favor of more than 40', 1, 0),
(35, 'sorcerer', 2, 'sorcerer', 'after 60 days to answer the question and in favor of more than 5 times', 1, 0),
(36, 'classification experts', 2, 'classification experts', 'label created the problem by using more than 50', 1, 0);


TYPE_ACTIVITY_ASK_QUESTION=1
TYPE_ACTIVITY_ANSWER=2
TYPE_ACTIVITY_COMMENT_QUESTION=3
TYPE_ACTIVITY_COMMENT_ANSWER=4
TYPE_ACTIVITY_UPDATE_QUESTION=5
TYPE_ACTIVITY_UPDATE_ANSWER=6
TYPE_ACTIVITY_PRIZE=7
TYPE_ACTIVITY_MARK_ANSWER=8
TYPE_ACTIVITY_VOTE_UP=9
TYPE_ACTIVITY_VOTE_DOWN=10
TYPE_ACTIVITY_CANCEL_VOTE=11
TYPE_ACTIVITY_DELETE_QUESTION=12
TYPE_ACTIVITY_DELETE_ANSWER=13
TYPE_ACTIVITY_MARK_OFFENSIVE=14
TYPE_ACTIVITY_UPDATE_TAGS=15
TYPE_ACTIVITY_FAVORITE=16
TYPE_ACTIVITY_USER_FULL_UPDATED = 17
"""

class Command(BaseCommand):
    def handle_noargs(self, **options):
        try:
            self.delete_question_be_voted_up_3()
            self.delete_answer_be_voted_up_3()
            self.delete_question_be_vote_down_3()
            self.delete_answer_be_voted_down_3()
            self.answer_be_voted_up_10()
            self.question_be_voted_up_10()
            self.question_view_1000()
            self.answer_self_question_be_voted_up_3()
            self.answer_be_voted_up_100()
            self.question_be_voted_up_100()
            self.question_be_favorited_100()
            self.question_view_10000()
            self.answer_be_voted_up_25()
            self.question_be_voted_up_25()
            self.question_be_favorited_25()
            self.question_view_2500()
            self.answer_be_accepted_and_voted_up_40()
            self.question_be_answered_after_60_days_and_be_voted_up_5()
            self.created_tag_be_used_in_question_50()
        except Exception, e:
            print e
        finally:
            connection.close()
    
    def delete_question_be_voted_up_3(self):
        """
        (1, '炼狱法师', 3, '炼狱法师', '删除自己有3个以上赞成票的帖子', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM activity act, question q WHERE act.object_id = q.id AND\
                act.activity_type = %s AND\
                q.vote_up_count >=3 AND \
                act.is_auditted = 0" % (TYPE_ACTIVITY_DELETE_QUESTION)
        self.__process_activities_badge(query, 1, Question)
        
    def delete_answer_be_voted_up_3(self):
        """
        (1, '炼狱法师', 3, '炼狱法师', '删除自己有3个以上赞成票的帖子', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM activity act, answer an WHERE act.object_id = an.id AND\
                act.activity_type = %s AND\
                an.vote_up_count >=3 AND \
                act.is_auditted = 0" % (TYPE_ACTIVITY_DELETE_ANSWER)
        self.__process_activities_badge(query, 1, Answer)
        
    def delete_question_be_vote_down_3(self):
        """
        (2, '压力白领', 3, '压力白领', '删除自己有3个以上反对票的帖子', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM activity act, question q WHERE act.object_id = q.id AND\
                act.activity_type = %s AND\
                q.vote_down_count >=3 AND \
                act.is_auditted = 0" % (TYPE_ACTIVITY_DELETE_QUESTION)
        content_type = ContentType.objects.get_for_model(Question)
        self.__process_activities_badge(query, 2, Question)

    def delete_answer_be_voted_down_3(self):
        """
        (2, '压力白领', 3, '压力白领', '删除自己有3个以上反对票的帖子', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM activity act, answer an WHERE act.object_id = an.id AND\
                act.activity_type = %s AND\
                an.vote_down_count >=3 AND \
                act.is_auditted = 0" % (TYPE_ACTIVITY_DELETE_ANSWER)
        self.__process_activities_badge(query, 2, Answer)
        
    def answer_be_voted_up_10(self):
        """
        (3, '优秀回答', 3, '优秀回答', '回答好评10次以上', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM \
                    activity act, answer a WHERE act.object_id = a.id AND\
                    act.activity_type = %s AND \
                    a.vote_up_count >= 10 AND\
                    act.is_auditted = 0" % (TYPE_ACTIVITY_ANSWER)
        self.__process_activities_badge(query, 3, Answer)
        
    def question_be_voted_up_10(self):
        """
        (4, '优秀问题', 3, '优秀问题', '问题好评10次以上', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM \
                    activity act, question q WHERE act.object_id = q.id AND\
                    act.activity_type = %s AND \
                    q.vote_up_count >= 10 AND\
                    act.is_auditted = 0" % (TYPE_ACTIVITY_ASK_QUESTION)
        self.__process_activities_badge(query, 4, Question)
    
    def question_view_1000(self):
        """
        (6, '流行问题', 3, '流行问题', '问题的浏览量超过1000人次', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM \
                    activity act, question q WHERE act.activity_type = %s AND\
                    act.object_id = q.id AND \
                    q.view_count >= 1000 AND\
                    act.object_id NOT IN \
                        (SELECT object_id FROM award WHERE award.badge_id = %s)" % (TYPE_ACTIVITY_ASK_QUESTION, 6)
        self.__process_activities_badge(query, 6, Question, False)
    
    def answer_self_question_be_voted_up_3(self):
        """
        (17, '自学成才', 3, '自学成才', '回答自己的问题并且有3个以上赞成票', 1, 0),
        """
        query = "SELECT act.id, act.user_id, act.object_id FROM \
                    activity act, answer an WHERE act.activity_type = %s AND\
                    act.object_id = an.id AND\
                    an.vote_up_count >= 3 AND\
                    act.user_id = (SELECT user_id FROM question q WHERE q.id = an.question_id) AND\
                    act.object_id NOT IN \
                        (SELECT object_id FROM award WHERE award.badge_id = %s)" % (TYPE_ACTIVITY_ANSWER, 17)
        self.__process_activities_badge(query, 17, Question, False)
    
    def answer_be_voted_up_100(self):
        """
        (18, '最有价值回答', 1, '最有价值回答', '回答超过100次赞成票', 1, 0),
        """
        query = "SELECT an.id, an.author_id FROM answer an WHERE an.vote_up_count >= 100 AND an.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (18)
        
        self.__process_badge(query, 18, Answer)
    
    def question_be_voted_up_100(self):
        """
        (19, '最有价值问题', 1, '最有价值问题', '问题超过100次赞成票', 1, 0),
        """
        query = "SELECT q.id, q.author_id FROM question q WHERE q.vote_up_count >= 100 AND q.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (19)
        
        self.__process_badge(query, 19, Question)
    
    def question_be_favorited_100(self):
        """
        (20, '万人迷', 1, '万人迷', '问题被100人以上收藏', 1, 0),
        """
        query = "SELECT q.id, q.author_id FROM question q WHERE q.favourite_count >= 100 AND q.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (20)
        
        self.__process_badge(query, 20, Question)

    def question_view_10000(self):
        """
        (21, '著名问题', 1, '著名问题', '问题的浏览量超过10000人次', 1, 0),
        """
        query = "SELECT q.id, q.author_id FROM question q WHERE q.view_count >= 10000 AND q.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (21)
        
        self.__process_badge(query, 21, Question)
    
    def answer_be_voted_up_25(self):
        """
        (23, '极好回答', 2, '极好回答', '回答超过25次赞成票', 1, 0),
        """
        query = "SELECT a.id, a.author_id FROM answer a WHERE a.vote_up_count >= 25 AND a.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (23)
        
        self.__process_badge(query, 23, Answer)
    
    def question_be_voted_up_25(self):
        """
        (24, '极好问题', 2, '极好问题', '问题超过25次赞成票', 1, 0),
        """
        query = "SELECT q.id, q.author_id FROM question q WHERE q.vote_up_count >= 25 AND q.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (24)
        
        self.__process_badge(query, 24, Question)
    
    def question_be_favorited_25(self):
        """
        (25, '受欢迎问题', 2, '受欢迎问题', '问题被25人以上收藏', 1, 0),
        """
        query = "SELECT q.id, q.author_id FROM question q WHERE q.favourite_count >= 25 AND q.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (25)
        
        self.__process_badge(query, 25, Question)
    
    def question_view_2500(self):
        """
        (31, '最受关注问题', 2, '最受关注问题', '问题的浏览量超过2500人次', 1, 0),
        """
        query = "SELECT q.id, q.author_id FROM question q WHERE q.view_count >= 2500 AND q.id NOT IN \
                (SELECT object_id FROM award WHERE award.badge_id = %s)" % (31)
        
        self.__process_badge(query, 31, Question)
    
    def answer_be_accepted_and_voted_up_40(self):
        """
        (34, '导师', 2, '导师', '被指定为最佳答案并且赞成票40以上', 1, 0),
        """
        query = "SELECT a.id, a.author_id FROM answer a WHERE a.vote_up_count >= 40 AND\
                    a.accepted = 1 AND\
                    a.id NOT IN \
                    (SELECT object_id FROM award WHERE award.badge_id = %s)" % (34)
        
        self.__process_badge(query, 34, Answer)
    
    def question_be_answered_after_60_days_and_be_voted_up_5(self):
        """
        (35, '巫师', 2, '巫师', '在提问60天之后回答并且赞成票5次以上', 1, 0),
        """
        query = "SELECT a.id, a.author_id FROM question q, answer a WHERE q.id = a.question_id AND\
                    DATEDIFF(a.added_at, q.added_at) >= 60 AND\
                    a.vote_up_count >= 5 AND \
                    a.id NOT IN \
                    (SELECT object_id FROM award WHERE award.badge_id = %s)" % (35)
        
        self.__process_badge(query, 35, Answer)
    
    def created_tag_be_used_in_question_50(self):
        """
        (36, '分类专家', 2, '分类专家', '创建的标签被50个以上问题使用', 1, 0);
        """
        query = "SELECT t.id, t.created_by_id FROM tag t, auth_user u WHERE t.created_by_id = u.id AND \
                    t. used_count >= 50 AND \
                    t.id NOT IN \
                    (SELECT object_id FROM award WHERE award.badge_id = %s)" % (36)
                    
        self.__process_badge(query, 36, Tag)
    
    def __process_activities_badge(self, query, badge, content_object, update_auditted=True):
        content_type = ContentType.objects.get_for_model(content_object)

        cursor = connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if update_auditted:
                activity_ids = []
            badge = get_object_or_404(Badge, id=badge)
            for row in rows:
                activity_id = row[0]
                user_id = row[1]
                object_id = row[2]
                
                user = get_object_or_404(User, id=user_id)
                award = Award(user=user, badge=badge, content_type=content_type, object_id=objet_id)
                award.save()
                
                if update_auditted:
                    activity_ids.append(activity_id)
                
            if update_auditted:
                self.update_activities_auditted(cursor, activity_ids)
        finally:
            cursor.close()
        
    def __process_badge(self, query, badge, content_object):
        content_type = ContentType.objects.get_for_model(Answer)
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            badge = get_object_or_404(Badge, id=badge)
            for row in rows:
                object_id = row[0]
                user_id = row[1]

                user = get_object_or_404(User, id=user_id)
                award = Award(user=user, badge=badge, content_type=content_type, object_id=object_id)
                award.save()
        finally:
            cursor.close()