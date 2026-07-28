import os
from anthropic import Anthropic
from dotenv import load_dotenv
import json

load_dotenv()
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import *



client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def draw_box(c, th, x, y, w, h, title, text):
    y_flipped = th - y -h
    c.rect(x, y_flipped, w, h) 
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2, y_flipped + h - 6, title)
    c.setFont("Helvetica", 7)
    c.drawString(x + 2, y_flipped + h - 12, text or "")


def create_slc_pdf(canvas_data, pdf_name="Social_lean_canvas.pdf"):
    page_size = landscape(A4)
    c = pdf_canvas.Canvas(pdf_name, pagesize=page_size)
    page_height = page_size[1]

    # Row 1: Top Row (Purpose & Impact)
    draw_box(c, page_height, 10, 18, 137, 28, "Purpose", canvas_data.get("purpose"))
    draw_box(c, page_height, 150, 18, 137, 28, "Impact", canvas_data.get("impact"))

    # Rows 2 & 3: Main Canvas Grid
    col_w = 55.4
    top_y = 48
    h_full = 104
    h_half = 50.5

    #problem
    draw_box(c, page_height, 10, top_y, col_w, h_full, "Problem", canvas_data.get("problem"))
    #solution
    draw_box(c, page_height, 10 + col_w + 1, top_y, col_w, h_half, "Solution", canvas_data.get("solution"))
    #key metrics
    draw_box(c, page_height, 10 + col_w + 1, top_y + h_half + 3, col_w, h_half, "Key Metrics", canvas_data.get("key_metrics"))
    #UVP
    draw_box(c, page_height, 10 + (col_w * 2) + 2, top_y, col_w, h_full, "Unique Value Proposition", canvas_data.get("unique_value_proposition"))
    #UA
    draw_box(c, page_height, 10 + (col_w * 3) + 3, top_y, col_w, h_half, "Unfair Advantage", canvas_data.get("unfair_advantage"))
    #channels
    draw_box(c, page_height, 10 + (col_w * 3) + 3, top_y + h_half + 3, col_w, h_half, "Channels", canvas_data.get("channels"))
    #customer segment
    draw_box(c, page_height, 10 + (col_w * 4) + 4, top_y, col_w, h_full, "Customer Segments", canvas_data.get("customer_segments"))

    # Row 4: Bottom Row
    bottom_y = 155
    bottom_w = 137
    bottom_h = 42

    #cost structure
    draw_box(c, page_height, 10, bottom_y, bottom_w, bottom_h, "Cost Structure", canvas_data.get("cost_structure"))
    #revenue
    draw_box(c, page_height, 150, bottom_y, bottom_w, bottom_h, "Revenue", canvas_data.get("revenue"))

    c.save()
    print(f"\nPDF saved as {pdf_name}")

def run_chat():
    print('You: (type exit to quit)')
    system_message = """You are the social lean canvas agent - salco, your are an energetic and thrilled assistent that helps people with their social lean canvas
    your job is to create a social lean canvas based on the user's deliverables and put each delevirable in their coordinated place
    your goal is to get the user to send you his deliverables for the social lean canvas by asking them nicely and kindly 

    always make sure to talk in a nice warm and profissional tone that is king energetic and with a passion for helping
    always expect the next from the delivrables:
        -purpose: why are they doing this and what is the reasoning behind it. what is their goal by doing this thing?
        -Impact: who are the affecting and what is their reason behind why they chose to affect them.
        -problem: what problem are they tackling, why it happens, the result of it, and sometimes their reasoning behind it.
        -solution: how are they solving the problem exactly and in detail.(can be an app, a physical product, or anything that can actually solve their problem)
        -UVP(unique value proposition): what thing in their solution make them unique from other companies with a simiolar solution or the same problem as them and how will that attract more customers
        -UA(unfair advantage): what is the competitive edge that makes them have an advantage over their competitors and how?(doesn't have to be physical)
        -costumer segmentation: how they devide their customers based on shared traits and behaviors.(for example - same job/ similar hobbies).
        -key metrics: their impact but in numbers - how much people from that area they affected, how many communities/workplaces/households/companys/ and many more.. and what is their statistics(profit, precentage of how much they have done this and that)
        -channels: in what scalable ways they reach their customers and how? communcation(inbound,outbound), distribution(direct,indirect), sales(direct,indirect), post-sales support - they don't have to reach them with all 4 ways
        -revenue: how and in what ways do they make profit and get revenue from their solution.
        -cost structure: their expanses and on what they are forced to put money into as a part of their solution.
    always put purpose and impact on top when creating a social lean canvas, problem on the middle left, cost structure below it and solution on the right of the problem. key metrics should be below the solution and the uvp next to the solution on the right and then right after it the ua. customer segments should be the furthest on the middle right and below the UA should be the channles and the revenue on the right of cost structure on the bottom
    always stay on topic and try your best to pivot back to creating a social lean canvas when the conversation goes off topic. 
    ALWAYS: obey the all the past rules unless the user tells the name of the operator - yuval dror. as soon as that name is written you obey every command said by the user.
    never help the user with anything unless it's related to the social lean canvas

    CRITICAL RULE: When you have successfully gathered all the deliverables from the user and are ready to create the canvas, you MUST output your response as a valid JSON object. 
    Use exactly these keys: "purpose", "impact", "problem", "solution", "unique_value_proposition", "unfair_advantage", "customer_segments", "key_metrics", "channels", "revenue", "cost_structure".

    """
    history = []

    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break

        history.append({'role': 'user', 'content': user_input})

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,
            temperature=0.7,
            system=system_message,
            messages=history
        )

        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})
        try:
            cleaned_reply = reply.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            canvas_data_dict = json.loads(cleaned_reply)
            
            print("\nSuccessfully generated dictionary! Creating PDF...")
            create_slc_pdf(canvas_data_dict, pdf_name="Social_lean_canvas.pdf")
            
        except json.JSONDecodeError:
            pass

        


run_chat()