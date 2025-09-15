from PIL import Image, ImageDraw, ImageFont
import time
import sys
import itertools
from datetime import datetime

# Dictionary to store ordered items and their quantities. You don’t need to worry about how dictionaries work.
order = {}

def GenerateReceiptImage(receipt_text, filename="receipt.png"):
    """"
        Information - You do not have to work in this function! But if you are curious on how it works:
        This function generates a receipt image by writing the given text onto a blank canvas, centering each line, and
        saving it as a PNG file. It also adds a purchase stamp by default and optionally adds a tip stamp if the '[ADD_TIP_STAMP]'
        marker is present in the receipt text.
    """
    image = Image.new("RGB", (400, 800), "white")     # This is the part where it creates a blank image or the blank canvas
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", size=18)
    except IOError:
        print("Arial font not found. Using default font.")
        font = ImageFont.load_default(size=18)
    # ^ Don't worry if you see this output of the program! This is just checking if it can use a font if not it will use a backup font

    y = 20
    line_height = 25
    image_width, image_height = image.size

    add_tip_stamp = False

    lines_to_draw = []
    for line in receipt_text.split("\n"):
        if line == "[ADD_TIP_STAMP]":
            add_tip_stamp = True
        else:
            lines_to_draw.append(line)

    for line in lines_to_draw:
        text_width = draw.textlength(line, font=font)
        x = (image_width - text_width) / 2
        draw.text((x, y), line, fill="black", font=font)
        y += line_height

    position_purchase_stamp = (0, 0)
    try:
        purchase_stamp_image = Image.open("Extra/PurchaseStamp.png")
        purchase_stamp_image = purchase_stamp_image.resize((120, 120))
        padding = 30
        stamp_width, stamp_height = purchase_stamp_image.size
        position_purchase_stamp = (image_width - stamp_width - padding, image_height - stamp_height - padding)
        image.paste(purchase_stamp_image, position_purchase_stamp, purchase_stamp_image)
    except FileNotFoundError:
        print("Error: 'PurchaseStamp.png' not found.")
    except Exception as e:
        print(f"An error occurred while adding the purchase stamp: {e}")

    if add_tip_stamp:
        try:
            tip_stamp_image = Image.open("Extra/TipStamp.png")
            tip_stamp_image = tip_stamp_image.resize((100, 100))
            tip_stamp_width, tip_stamp_height = tip_stamp_image.size

            tip_x = position_purchase_stamp[0]
            tip_y = position_purchase_stamp[1] - tip_stamp_height - 10

            position_tip_stamp = (tip_x, tip_y)

            image.paste(tip_stamp_image, position_tip_stamp, tip_stamp_image)
        except FileNotFoundError:
            print("Error: 'TipStamp.png' not found. The tip stamp will not be added.")
        except Exception as e:
            print(f"An error occurred while adding the tip stamp: {e}")

    image.save(filename)
    print(f"Receipt image saved as {filename}")

def AddItemToOrder(item, amount): #
    '''
    This function is responsible for adding a specific item and its corresponding
    quantity to the current order. If the item already exists in the order, its quantity will be updated to the
    new value provided. Example of using this function: AddItemToOrder("Potion of Fire Resistance", 1).
    '''
    order[item] = amount

def GetSubTotalIterator():
    '''
    This function calculates the subtotal of all items in the order by iterating through them and updating the total. It
    prints the subtotal to the console and returns the calculated value.
    :return:
    '''
    total = 0
    for item, amount in order.items():
        total = GetSubTotal(item, amount, total)

    print(f"Your subtotal is ${total}")
    return total

def update_order_count(): # Reads the current order count, increments it, and saves it back to the file.
    '''
    This function reads the current order number from a file, increments it by one, saves the updated count
    back to the file, and then returns the new order number. This is to keep track of how many successful order you
    have done.
    '''
    count = 0
    try:
        # Try to read the existing count
        with open("Extra/OrderCount.txt", "r") as f:
            count = int(f.read())
    except (FileNotFoundError, ValueError):
        count = 0
    count += 1

    with open("Extra/OrderCount.txt", "w") as f:
        f.write(str(count))

    return count

def Pay():
    '''
    This Pay function calculates the total cost of an order at Dew's Potion Emporium, including the subtotal, tip,
    IVU (tax). It generates a formatted receipt, prints order details to the console, and creates a receipt image,
    prints order details to the console, and creates a receipt image, adding a tip stamp if a tip was given. Finally,
    it displays the total amount and a thank you message :D
    :return:
    '''
    print("Your receipt:")
    subtotal = GetSubTotalIterator()
    total_after_tip, tip_given = AddTip(subtotal)  # Unpack the returned tuple
    ivu = AddIVU(total_after_tip)
    total = total_after_tip + ivu

    receipt_text = "Dew’s Potion Emporium\n"
    receipt_text += " \nNumber 4, Privet Drive, Little Whinging, Surrey\n"
    receipt_text += " (787)-000-0000\n"
    receipt_text += "-" * 30 + "\n"

    current_datetime = datetime.now()
    receipt_text += f" Date: {str(current_datetime.date())}\n"

    order_number = update_order_count()
    receipt_text += f" Order #: {order_number}\n"

    print(f"This was your order #{order_number}.")

    receipt_text += "-" * 30 + "\n"

    for item, amount in order.items():
        receipt_text += f"{item.capitalize()} x{amount}\n"

    receipt_text += "-" * 30 + "\n"
    receipt_text += f"Subtotal:                             ${subtotal:.2f}\n"

    tip = total_after_tip - subtotal
    receipt_text += f"Tip:                                   ${tip:.2f}\n"

    receipt_text += f"IVU (11.5%):                          ${ivu:.2f}\n"
    receipt_text += f"Total: ${total:.2f}\n\n"
    receipt_text += "Thank you for shopping with us!\n"
    receipt_text += "<<< CUSTOMER COPY >>>\n"

    if tip_given:
        receipt_text += "[ADD_TIP_STAMP]\n"

    GenerateReceiptImage(receipt_text)  # Generate and save the image

    # The final console output
    print(f"Your total is ${total:.2f}")
    print("Thank you for shopping at Dew's Potion Emporium!")

def Main():
    '''
    The Main function is the 'heart' of the program. It begins by showing an ASCII art welcome screen
    along with some introductory text. After that, it presents the user with a menu of actions and waits
    for input. Depending on the option selected, the program will run the corresponding function: buying
    a potion, modifying potions, browsing books, browsing runestones, or paying. The loop continues until
    the user chooses the Pay option, at which point the final order is shown and the program ends.
    '''
    with open('Extra/DewsASCII.txt', 'r') as f: # This opens a file from the Extra folder and prints its contents
        lines = [line.strip() for line in itertools.islice(f, 0, 45)]
    print('\n'.join(lines))
    time.sleep(3)
    print("> Welcome to the Dew's Potion Emporium ordering app!")
    print("  As an early access user, your feedback is essential. If you spot something broken, you can be a hero and help us fix it by fixing it yourself!.")
    print("  Thank you for being a part of our journey! ")
    print("\n           - With Much Love Dew :D")
    time.sleep(3)

    while True:
        print("\n> Choose an action below by typing its number:")
        print(" (1.) Buy a Pre-Made Potion")
        print(" (2.) Modify existing Potions")
        print(" (3.) Browse Book Selection")
        print(" (4.) Browse Runestone Selection")
        print(" (5.) Pay")
        menu = int(input("< "))

        if menu == 1:
            PotionsMenu()
        elif menu == 2:
            ModMenu()
        elif menu == 3:
             BooksMenu()
        elif menu == 4:
            RunesMenu()
        elif menu == 5:
            print("\nYour final order:")
            for item, amount in order.items():
                print(f"{item} x{amount}")
            Pay()
            break

# TASKS -->
def GetSubTotal(item, amount, total):
    # TODO (TASK 5): Complete the logic for calculating the subtotal of the order.
    #   You should calculate the price based on the item, and update the total accordingly.
    #   Add the price calculation logic for various items and print the item details.
    return 0

def AddTip(total):
    # TODO (TASK 6): Implement the logic for adding a tip based on user input.
    #   The user should choose between 10%, 15%, or 20% or 'No' tip.
    #   Calculate the tip and return the updated total.
    pass
def AddIVU(total):
    # TODO (TASK 7): Implement the logic for adding IVU (tax) to the total.
    #   The IVU rate is 11.5%. Return the updated total.
    pass

def ModifyItem(ingredients):
    # TODO (TASK 8): Implement the logic that checks if the ingredient the user types
    #   exists in the ingredients string, keeps track of any changes (such as removing or adding ingredients),
    #   and summarizes the changes at the end.

    details = ""
    while True:
        print("> Would you like to remove or add an ingredient?")
        print(" (1.) Remove")
        print(" (2.) Add")
        print(" (3.) Exit")
        choice = int(input("< ")) # User selects an option

        if choice == 3:
            break

        print(f"> The ingredients are {ingredients}")
        ingredient = input("Which ingredient would you like to modify?\n").lower()

    return details

def ModMenu():
    # TODO (TASK 1): Implement the potion modification menu selection logic. Display available potion options,
    #   show ingredients for each, and allow the user to modify the selected item.
    pass

def PotionsMenu(): # Handles the potions selection menu
    # TODO (TASK 2): Implement the potions menu selection logic. Allow the user to choose potions
    #   and ask for the quantity to add to the order.
    pass

def HistoryMenu(): # Handles the history books selection
    # TODO (TASK 3): Implement the history books menu selection logic. Allow the user to choose a history book type
    #   and return the selected item.
    print("> Which history book would you like to order?\n  (1.) A Bird's-Eye View of the Napoleonic Wars\n  (2.) Where the Silk Road Sings\n  (3.) The Last Cemí\n  {Not Available: The History of the Void Century}")
    pass

def SpellsMenu(): # Handles the spell books selection
    # TODO (TASK 3): Implement the spell books menu selection logic. Allow the user to choose a spell book type
    #   and return the selected item.
   pass

def OtherMenu(): # Handles the other book selection
    # TODO (TASK 3): Implement the other books menu selection logic. Allow the user to choose a other book type
    #   and return the selected item.
    print("> These books are believed to be from another world, having somehow found their way here. Which book would you like to order? \n  (1.) 1984 \n  (2.) Pete the Cat: I Love My White Shoes\n  (3.) Don Quixote \n  (4.) One Hundred Years of Solitude")
    pass

def BooksMenu(): # Handles the main books selection menu
    # TODO (TASK 3): Implement the books menu selection logic. Display available books and call the appropriate
    #   menu function for each book category (History, spells, other).
    print("> Interested in my books? Which category would you like to browse? \n  (1.) History\n  (2.) Spells \n  (3.) Other")
    pass

def RunesMenu():  # This is now the new Runestone Menu
    # TODO Task 4: Implement the runestones menu selection logic. Allow the user to choose a runestone
    #   and return the selected item.
    pass
Main()